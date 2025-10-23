"""
Pytest configuration and fixtures for Stitch Shield Integration tests.
"""
import pytest
import boto3
import os
import json
import time
from moto import mock_s3, mock_dynamodb, mock_ssm, mock_lambda
from unittest.mock import patch, MagicMock


@pytest.fixture
def api_url():
    """Base API URL for testing."""
    return os.environ.get('TEST_API_URL', 'https://api-dev.stitch.urgd.dev/v1')


@pytest.fixture
def aws_region():
    """AWS region for testing."""
    return os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')


@pytest.fixture
def test_environment():
    """Test environment variables."""
    return {
        'STITCH_PROCESSING_BUCKET': 'urgd-stitch-processing-dev-123456789',
        'STITCH_STORAGE_BUCKET': 'urgd-stitch-storage-dev-123456789',
        'STATUS_TABLE_NAME': 'urgd-stitch-conversion-status-dev',
        'SHIELD_BUCKET_NAME': 'urgd-shield-quarantine-prod-123456789',
        'CONVERTER_LAMBDA_ARN': 'arn:aws:lambda:us-west-2:123456789:function:urgd-stitch-svg-converter-dev'
    }


@pytest.fixture
def mock_ssm_parameters():
    """Mock SSM parameters for testing."""
    return {
        '/urgd/shield/quarantine_bucket_name': 'urgd-shield-quarantine-prod-123456789'
    }


@pytest.fixture
def clean_svg_content():
    """Clean SVG content for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
</svg>'''


@pytest.fixture
def eicar_svg_content():
    """EICAR test string wrapped in SVG for malware testing."""
    eicar_string = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="50" font-family="Arial" font-size="12">{eicar_string}</text>
</svg>'''


@pytest.fixture
def mock_guardduty_event_clean():
    """Mock GuardDuty event for clean file."""
    return {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "GuardDuty Malware Protection Scan Status",
        "source": "aws.guardduty",
        "account": "123456789",
        "time": "2024-01-01T00:00:00Z",
        "region": "us-west-2",
        "detail": {
            "scanResult": "CLEAN",
            "s3ObjectArn": "arn:aws:s3:::urgd-shield-quarantine-prod-123456789/stitch/test-request-id/upload.svg",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }


@pytest.fixture
def mock_guardduty_event_infected():
    """Mock GuardDuty event for infected file."""
    return {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "GuardDuty Malware Protection Scan Status",
        "source": "aws.guardduty",
        "account": "123456789",
        "time": "2024-01-01T00:00:00Z",
        "region": "us-west-2",
        "detail": {
            "scanResult": {
                "threatName": "EICAR-Test-File",
                "threatType": "Malware",
                "severity": "HIGH"
            },
            "s3ObjectArn": "arn:aws:s3:::urgd-shield-quarantine-prod-123456789/stitch/test-request-id/upload.svg",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }


@pytest.fixture
def mock_s3_metadata():
    """Mock S3 object metadata for testing."""
    return {
        'app-name': 'stitch',
        'request-id': 'test-request-id',
        'destination-bucket': 'urgd-stitch-processing-dev-123456789',
        'upload-timestamp': '2024-01-01T00:00:00Z'
    }


class MockContext:
    """Mock Lambda context for testing."""
    def __init__(self):
        self.function_name = 'test-function'
        self.function_version = '$LATEST'
        self.invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789:function:test-function'
        self.memory_limit_in_mb = 128
        self.remaining_time_in_millis = 30000
        self.aws_request_id = 'test-request-id'
        self.log_group_name = '/aws/lambda/test-function'
        self.log_stream_name = '2024/01/01/[$LATEST]test-stream'


@pytest.fixture
def mock_lambda_context():
    """Mock Lambda context for testing."""
    return MockContext()


@pytest.fixture
def mock_dynamodb_item():
    """Mock DynamoDB item for testing."""
    return {
        'request_id': 'test-request-id',
        'status': 'uploading',
        'timestamp': '2024-01-01T00:00:00Z',
        'ttl': 1704067200
    }
