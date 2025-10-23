"""
Test suite for Shield integration end-to-end functionality.
"""
import pytest
import boto3
import json
import requests
import time
from moto import mock_s3, mock_dynamodb, mock_lambda, mock_ssm
from unittest.mock import patch, MagicMock
import os
import sys

# Add the lambdas directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambdas'))

from status_checker import lambda_handler as status_checker_handler
from shield_callback import lambda_handler as shield_callback_handler


class TestShieldIntegration:
    """Test Shield integration end-to-end functionality."""
    
    @mock_s3
    @mock_dynamodb
    @mock_ssm
    @patch.dict(os.environ, {
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev',
        'STITCH_STORAGE_BUCKET': 'urgd-stitch-storage-dev-123456789',
        'SHIELD_BUCKET_NAME': 'urgd-shield-quarantine-prod-123456789',
        'STITCH_PROCESSING_BUCKET': 'urgd-stitch-processing-dev-123456789',
        'CONVERTER_LAMBDA_ARN': 'arn:aws:lambda:us-west-2:123456789:function:urgd-stitch-svg-converter-dev'
    })
    def test_clean_file_flow(self, mock_dynamodb_item, mock_guardduty_event_clean, 
                           mock_s3_metadata, clean_svg_content):
        """Test complete flow for clean file processing."""
        
        # Setup mocked services
        s3_client = boto3.client('s3', region_name='us-west-2')
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        lambda_client = boto3.client('lambda', region_name='us-west-2')
        
        # Create DynamoDB table
        table = dynamodb.create_table(
            TableName='urgd-stitch-conversion-status-dev',
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create S3 buckets
        s3_client.create_bucket(
            Bucket='urgd-shield-quarantine-prod-123456789',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        s3_client.create_bucket(
            Bucket='urgd-stitch-processing-dev-123456789',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        s3_client.create_bucket(
            Bucket='urgd-stitch-storage-dev-123456789',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        
        # Create test file in Shield bucket with metadata
        test_key = 'stitch/test-request-id/upload.svg'
        s3_client.put_object(
            Bucket='urgd-shield-quarantine-prod-123456789',
            Key=test_key,
            Body=clean_svg_content,
            ContentType='image/svg+xml',
            Metadata=mock_s3_metadata
        )
        
        # Create initial status record
        table.put_item(Item=mock_dynamodb_item)
        
        # Mock Lambda invoke for converter
        with patch.object(lambda_client, 'invoke') as mock_invoke:
            mock_invoke.return_value = {'StatusCode': 202}
            
            # Test shield callback processing
            context = MagicMock()
            response = shield_callback_handler(mock_guardduty_event_clean, context)
            
            assert response['statusCode'] == 200
            
            # Verify file was moved to processing bucket
            try:
                s3_client.head_object(
                    Bucket='urgd-stitch-processing-dev-123456789',
                    Key='processing/test-request-id/upload.svg'
                )
                file_moved = True
            except:
                file_moved = False
            
            assert file_moved, "File should be moved to processing bucket"
            
            # Verify file was deleted from Shield bucket
            try:
                s3_client.head_object(
                    Bucket='urgd-shield-quarantine-prod-123456789',
                    Key=test_key
                )
                file_deleted = False
            except:
                file_deleted = True
            
            assert file_deleted, "File should be deleted from Shield bucket"
            
            # Verify status was updated
            status_response = table.get_item(Key={'request_id': 'test-request-id'})
            assert 'Item' in status_response
            assert status_response['Item']['status'] == 'converting'
            
            # Verify converter Lambda was invoked
            mock_invoke.assert_called_once()
            call_args = mock_invoke.call_args
            assert call_args[1]['FunctionName'] == 'arn:aws:lambda:us-west-2:123456789:function:urgd-stitch-svg-converter-dev'
            assert call_args[1]['InvocationType'] == 'Event'
    
    @mock_s3
    @mock_dynamodb
    @mock_ssm
    @patch.dict(os.environ, {
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev',
        'STITCH_STORAGE_BUCKET': 'urgd-stitch-storage-dev-123456789',
        'SHIELD_BUCKET_NAME': 'urgd-shield-quarantine-prod-123456789',
        'STITCH_PROCESSING_BUCKET': 'urgd-stitch-processing-dev-123456789',
        'CONVERTER_LAMBDA_ARN': 'arn:aws:lambda:us-west-2:123456789:function:urgd-stitch-svg-converter-dev'
    })
    def test_infected_file_flow(self, mock_dynamodb_item, mock_guardduty_event_infected,
                              mock_s3_metadata, eicar_svg_content):
        """Test complete flow for infected file processing."""
        
        # Setup mocked services
        s3_client = boto3.client('s3', region_name='us-west-2')
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        
        # Create DynamoDB table
        table = dynamodb.create_table(
            TableName='urgd-stitch-conversion-status-dev',
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create S3 buckets
        s3_client.create_bucket(
            Bucket='urgd-shield-quarantine-prod-123456789',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        s3_client.create_bucket(
            Bucket='urgd-stitch-processing-dev-123456789',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        
        # Create test file in Shield bucket with metadata
        test_key = 'stitch/test-request-id/upload.svg'
        s3_client.put_object(
            Bucket='urgd-shield-quarantine-prod-123456789',
            Key=test_key,
            Body=eicar_svg_content,
            ContentType='image/svg+xml',
            Metadata=mock_s3_metadata
        )
        
        # Create initial status record
        table.put_item(Item=mock_dynamodb_item)
        
        # Test shield callback processing
        context = MagicMock()
        response = shield_callback_handler(mock_guardduty_event_infected, context)
        
        assert response['statusCode'] == 200
        
        # Verify file was deleted from Shield bucket
        try:
            s3_client.head_object(
                Bucket='urgd-shield-quarantine-prod-123456789',
                Key=test_key
            )
            file_deleted = False
        except:
            file_deleted = True
        
        assert file_deleted, "Infected file should be deleted from Shield bucket"
        
        # Verify no file was moved to processing bucket
        try:
            s3_client.head_object(
                Bucket='urgd-stitch-processing-dev-123456789',
                Key='processing/test-request-id/upload.svg'
            )
            file_moved = True
        except:
            file_moved = False
        
        assert not file_moved, "Infected file should not be moved to processing bucket"
        
        # Verify status was updated to infected
        status_response = table.get_item(Key={'request_id': 'test-request-id'})
        assert 'Item' in status_response
        assert status_response['Item']['status'] == 'infected'
        assert 'scan_result' in status_response['Item']
    
    @mock_dynamodb
    @patch.dict(os.environ, {
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev',
        'STITCH_STORAGE_BUCKET': 'urgd-stitch-storage-dev-123456789'
    })
    def test_status_checker_ready(self, mock_dynamodb_item):
        """Test status checker for ready conversion."""
        
        # Setup DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName='urgd-stitch-conversion-status-dev',
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create ready status item
        ready_item = mock_dynamodb_item.copy()
        ready_item.update({
            'status': 'converted',
            'pes_key': 'converted/test-request-id.pes',
            'stitch_count': 1500,
            'quality': 'high'
        })
        table.put_item(Item=ready_item)
        
        # Test status checker
        event = {'pathParameters': {'request_id': 'test-request-id'}}
        context = MagicMock()
        
        with patch('boto3.client') as mock_s3_client:
            mock_s3 = mock_s3_client.return_value
            mock_s3.generate_presigned_url.return_value = 'https://test-download-url.com'
            
            response = status_checker_handler(event, context)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['status'] == 'ready'
            assert 'download_url' in body
            assert body['stitch_count'] == 1500
            assert body['quality'] == 'high'
    
    @mock_dynamodb
    @patch.dict(os.environ, {
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev',
        'STITCH_STORAGE_BUCKET': 'urgd-stitch-storage-dev-123456789'
    })
    def test_status_checker_infected(self, mock_dynamodb_item):
        """Test status checker for infected file."""
        
        # Setup DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName='urgd-stitch-conversion-status-dev',
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create infected status item
        infected_item = mock_dynamodb_item.copy()
        infected_item.update({
            'status': 'infected',
            'scan_result': '{"threatName": "EICAR-Test-File", "severity": "HIGH"}'
        })
        table.put_item(Item=infected_item)
        
        # Test status checker
        event = {'pathParameters': {'request_id': 'test-request-id'}}
        context = MagicMock()
        
        response = status_checker_handler(event, context)
        
        assert response['statusCode'] == 403
        body = json.loads(response['body'])
        assert body['status'] == 'infected'
        assert 'malware' in body['message'].lower()
    
    @mock_dynamodb
    @patch.dict(os.environ, {
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev',
        'STITCH_STORAGE_BUCKET': 'urgd-stitch-storage-dev-123456789'
    })
    def test_status_checker_processing(self, mock_dynamodb_item):
        """Test status checker for processing status."""
        
        # Setup DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName='urgd-stitch-conversion-status-dev',
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create processing status item
        processing_item = mock_dynamodb_item.copy()
        processing_item.update({'status': 'converting'})
        table.put_item(Item=processing_item)
        
        # Test status checker
        event = {'pathParameters': {'request_id': 'test-request-id'}}
        context = MagicMock()
        
        response = status_checker_handler(event, context)
        
        assert response['statusCode'] == 202
        body = json.loads(response['body'])
        assert body['status'] == 'converting'
        assert 'Converting' in body['message']
    
    @mock_dynamodb
    @patch.dict(os.environ, {
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev',
        'STITCH_STORAGE_BUCKET': 'urgd-stitch-storage-dev-123456789'
    })
    def test_status_checker_not_found(self):
        """Test status checker for non-existent request."""
        
        # Setup DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName='urgd-stitch-conversion-status-dev',
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Test status checker with non-existent request
        event = {'pathParameters': {'request_id': 'non-existent-id'}}
        context = MagicMock()
        
        response = status_checker_handler(event, context)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['status'] == 'not_found'


class TestShieldIntegrationEndToEnd:
    """Integration tests that require actual AWS services."""
    
    def test_clean_file_upload_flow(self, api_url, clean_svg_content):
        """Test complete clean file upload and processing flow."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Step 1: Get presigned URL
        url_response = requests.get(f"{api_url}/upload-url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        request_id = url_data['request_id']
        
        # Step 2: Upload file
        files = {'file': ('test.svg', clean_svg_content, 'image/svg+xml')}
        data = url_data['fields']
        
        upload_response = requests.post(url_data['upload_url'], data=data, files=files)
        assert upload_response.status_code in [200, 204]
        
        # Step 3: Poll for status (with timeout)
        max_attempts = 60  # 2 minutes with 2-second intervals
        for i in range(max_attempts):
            time.sleep(2)
            
            status_response = requests.get(f"{api_url}/status/{request_id}")
            assert status_response.status_code in [200, 202]
            
            status_data = status_response.json()
            status = status_data['status']
            
            if status == 'ready':
                assert 'download_url' in status_data
                assert status_data['stitch_count'] > 0
                assert 'quality' in status_data
                return  # Success!
            elif status == 'infected':
                pytest.fail("Clean file was incorrectly detected as infected")
            elif status == 'failed':
                pytest.fail(f"Conversion failed: {status_data.get('error', 'Unknown error')}")
        
        pytest.fail("Conversion timeout - file did not complete processing")
    
    def test_eicar_malware_detection(self, api_url, eicar_svg_content):
        """Test EICAR malware detection and rejection."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Step 1: Get presigned URL
        url_response = requests.get(f"{api_url}/upload-url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        request_id = url_data['request_id']
        
        # Step 2: Upload EICAR file
        files = {'file': ('eicar.svg', eicar_svg_content, 'image/svg+xml')}
        data = url_data['fields']
        
        upload_response = requests.post(url_data['upload_url'], data=data, files=files)
        assert upload_response.status_code in [200, 204]
        
        # Step 3: Poll for status (should detect as infected)
        max_attempts = 30  # 1 minute with 2-second intervals
        for i in range(max_attempts):
            time.sleep(2)
            
            status_response = requests.get(f"{api_url}/status/{request_id}")
            assert status_response.status_code in [200, 202, 403]
            
            status_data = status_response.json()
            status = status_data['status']
            
            if status == 'infected':
                assert 'malware' in status_data['message'].lower()
                return  # Success - malware detected!
            elif status == 'ready':
                pytest.fail("EICAR file was incorrectly processed as clean")
            elif status == 'failed':
                pytest.fail(f"Unexpected failure: {status_data.get('error', 'Unknown error')}")
        
        pytest.fail("Malware detection timeout - EICAR file was not detected")
    
    def test_status_polling_workflow(self, api_url, clean_svg_content):
        """Test status polling workflow with different states."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Get presigned URL and upload file
        url_response = requests.get(f"{api_url}/upload-url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        request_id = url_data['request_id']
        
        files = {'file': ('test.svg', clean_svg_content, 'image/svg+xml')}
        data = url_data['fields']
        
        upload_response = requests.post(url_data['upload_url'], data=data, files=files)
        assert upload_response.status_code in [200, 204]
        
        # Track status progression
        statuses_seen = []
        max_attempts = 30
        
        for i in range(max_attempts):
            time.sleep(2)
            
            status_response = requests.get(f"{api_url}/status/{request_id}")
            assert status_response.status_code in [200, 202]
            
            status_data = status_response.json()
            status = status_data['status']
            
            if status not in statuses_seen:
                statuses_seen.append(status)
            
            if status == 'ready':
                # Verify we saw expected status progression
                expected_statuses = ['uploading', 'scanning', 'converting']
                for expected in expected_statuses:
                    if expected in statuses_seen:
                        break
                else:
                    # At least one expected status should have been seen
                    assert len(statuses_seen) > 1, f"Expected status progression, got: {statuses_seen}"
                
                return  # Success!
            elif status == 'infected':
                pytest.fail("Clean file was incorrectly detected as infected")
            elif status == 'failed':
                pytest.fail(f"Conversion failed: {status_data.get('error', 'Unknown error')}")
        
        pytest.fail(f"Status polling timeout. Statuses seen: {statuses_seen}")
