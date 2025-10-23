"""
Test suite for presigned URL generation and upload functionality.
"""
import pytest
import boto3
import json
import requests
from moto import mock_s3, mock_ssm, mock_dynamodb
from unittest.mock import patch, MagicMock
import os
import sys

# Add the lambdas directory to the path so we can import the functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambdas'))

from upload_url_generator import lambda_handler as upload_url_handler


class TestPresignedURLGeneration:
    """Test presigned URL generation functionality."""
    
    @mock_s3
    @mock_ssm
    @mock_dynamodb
    @patch.dict(os.environ, {
        'STITCH_PROCESSING_BUCKET': 'urgd-stitch-processing-dev-123456789',
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev'
    })
    def test_presigned_url_generation(self, mock_ssm_parameters, test_environment):
        """Test that presigned URL generation works correctly."""
        
        # Setup mocked services
        ssm_client = boto3.client('ssm', region_name='us-west-2')
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        
        # Create SSM parameter
        ssm_client.put_parameter(
            Name='/urgd/shield/quarantine_bucket_name',
            Value='urgd-shield-quarantine-prod-123456789',
            Type='String'
        )
        
        # Create DynamoDB table
        table = dynamodb.create_table(
            TableName='urgd-stitch-conversion-status-dev',
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create S3 bucket (for presigned URL generation)
        s3_client = boto3.client('s3', region_name='us-west-2')
        s3_client.create_bucket(
            Bucket='urgd-shield-quarantine-prod-123456789',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        
        # Test the Lambda function
        event = {}
        context = MagicMock()
        
        response = upload_url_handler(event, context)
        
        # Verify response structure
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        
        body = json.loads(response['body'])
        assert 'upload_url' in body
        assert 'fields' in body
        assert 'request_id' in body
        assert 'expires_in' in body
        assert body['expires_in'] == 300
        
        # Verify fields contain required metadata
        fields = body['fields']
        assert fields['x-amz-meta-app-name'] == 'stitch'
        assert 'x-amz-meta-request-id' in fields
        assert fields['x-amz-meta-destination-bucket'] == 'urgd-stitch-processing-dev-123456789'
        assert 'x-amz-meta-upload-timestamp' in fields
        assert fields['Content-Type'] == 'image/svg+xml'
        
        # Verify DynamoDB record was created
        table = dynamodb.Table('urgd-stitch-conversion-status-dev')
        response = table.get_item(Key={'request_id': body['request_id']})
        assert 'Item' in response
        assert response['Item']['status'] == 'uploading'
    
    @mock_s3
    @mock_ssm
    @mock_dynamodb
    @patch.dict(os.environ, {
        'STITCH_PROCESSING_BUCKET': 'urgd-stitch-processing-dev-123456789',
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev'
    })
    def test_presigned_url_ssm_error(self, mock_ssm_parameters, test_environment):
        """Test error handling when SSM parameter is missing."""
        
        # Don't create the SSM parameter - this should cause an error
        event = {}
        context = MagicMock()
        
        response = upload_url_handler(event, context)
        
        # Verify error response
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Failed to generate upload URL' in body['error']
    
    def test_presigned_url_validation(self, api_url):
        """Test presigned URL validation (requires actual API)."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Test presigned URL generation
        response = requests.get(f"{api_url}/upload-url")
        assert response.status_code == 200
        
        data = response.json()
        assert 'upload_url' in data
        assert 'fields' in data
        assert 'request_id' in data
        assert 'expires_in' in data
        
        # Verify URL is valid S3 presigned POST
        assert data['upload_url'].startswith('https://')
        assert 's3' in data['upload_url']
        assert 'amazonaws.com' in data['upload_url']
        
        # Verify fields structure
        fields = data['fields']
        required_fields = [
            'key', 'AWSAccessKeyId', 'policy', 'signature',
            'x-amz-meta-app-name', 'x-amz-meta-request-id',
            'x-amz-meta-destination-bucket', 'x-amz-meta-upload-timestamp',
            'Content-Type'
        ]
        
        for field in required_fields:
            assert field in fields, f"Missing required field: {field}"
        
        # Verify metadata values
        assert fields['x-amz-meta-app-name'] == 'stitch'
        assert fields['x-amz-meta-destination-bucket'] is not None
        assert fields['Content-Type'] == 'image/svg+xml'
        
        # Verify request_id is valid UUID format
        request_id = data['request_id']
        assert len(request_id) == 36  # UUID4 length
        assert request_id.count('-') == 4  # UUID4 format


class TestPresignedUpload:
    """Test actual file upload using presigned URLs."""
    
    def test_clean_file_upload(self, api_url, clean_svg_content):
        """Test uploading a clean SVG file."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Step 1: Get presigned URL
        url_response = requests.get(f"{api_url}/upload-url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        
        # Step 2: Upload file using presigned URL
        files = {'file': ('test.svg', clean_svg_content, 'image/svg+xml')}
        data = url_data['fields']
        
        upload_response = requests.post(url_data['upload_url'], data=data, files=files)
        assert upload_response.status_code in [200, 204]
        
        # Step 3: Verify we can check status
        request_id = url_data['request_id']
        status_response = requests.get(f"{api_url}/status/{request_id}")
        assert status_response.status_code in [200, 202]  # 202 for processing
        
        status_data = status_response.json()
        assert 'status' in status_data
        assert status_data['status'] in ['uploading', 'scanning', 'converting', 'ready', 'failed']
    
    def test_upload_with_invalid_content_type(self, api_url):
        """Test that upload fails with invalid content type."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Get presigned URL
        url_response = requests.get(f"{api_url}/upload-url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        
        # Try to upload with wrong content type
        files = {'file': ('test.txt', 'not an svg', 'text/plain')}
        data = url_data['fields']
        
        upload_response = requests.post(url_data['upload_url'], data=data, files=files)
        # Should fail due to content type validation
        assert upload_response.status_code in [400, 403]
    
    def test_upload_with_oversized_file(self, api_url):
        """Test that upload fails with oversized file."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Get presigned URL
        url_response = requests.get(f"{api_url}/upload-url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        
        # Create oversized content (>10MB)
        oversized_content = 'x' * (11 * 1024 * 1024)  # 11MB
        files = {'file': ('test.svg', oversized_content, 'image/svg+xml')}
        data = url_data['fields']
        
        upload_response = requests.post(url_data['upload_url'], data=data, files=files)
        # Should fail due to size validation
        assert upload_response.status_code in [400, 413]
    
    def test_upload_expiration(self, api_url, clean_svg_content):
        """Test that presigned URL expires after 5 minutes."""
        if not api_url.startswith('https://api-dev'):
            pytest.skip("Skipping integration test - not in dev environment")
        
        # Get presigned URL
        url_response = requests.get(f"{api_url}/upload-url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        
        # Verify expiration time
        assert url_data['expires_in'] == 300  # 5 minutes
        
        # Note: We can't easily test actual expiration in unit tests
        # This would require waiting 5+ minutes, which is impractical
        # In integration tests, this would be tested with a shorter expiration
