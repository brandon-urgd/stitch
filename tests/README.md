# Stitch Shield Integration Test Suite

This directory contains comprehensive tests for the Shield integration functionality in Stitch.

## Test Structure

### Unit Tests
- **`test_presigned_upload.py`** - Tests for presigned URL generation and upload validation
- **`test_shield_integration.py`** - Tests for Shield callback processing and status checking

### Test Fixtures
- **`fixtures/clean_test.svg`** - Clean SVG file for testing normal processing
- **`fixtures/eicar_wrapped.svg`** - EICAR test string wrapped in SVG for malware testing

### Configuration
- **`conftest.py`** - Pytest fixtures and configuration
- **`pytest.ini`** - Pytest configuration and markers
- **`requirements.txt`** - Test dependencies
- **`run_tests.py`** - Test runner script

## Test Categories

### Unit Tests (Mocked AWS Services)
These tests use `moto` to mock AWS services and can run without actual AWS credentials:

- Presigned URL generation
- DynamoDB status tracking
- S3 operations
- Lambda function logic
- Error handling

### Integration Tests (Real AWS Services)
These tests require actual AWS credentials and a deployed Stitch dev environment:

- End-to-end file upload flow
- Malware detection with EICAR
- Status polling workflow
- Real API endpoint testing

## Running Tests

### Prerequisites

1. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. For integration tests, set environment variables:
   ```bash
   export TEST_API_URL=https://api-dev.stitch.urgd.dev/v1
   export AWS_DEFAULT_REGION=us-west-2
   ```

### Running Tests

#### Unit Tests Only
```bash
python run_tests.py --unit
# or
pytest -m unit
```

#### Integration Tests Only
```bash
python run_tests.py --integration
# or
pytest -m integration
```

#### All Tests
```bash
python run_tests.py --all
# or
pytest
```

#### Specific Test Files
```bash
pytest test_presigned_upload.py
pytest test_shield_integration.py
```

#### Specific Test Functions
```bash
pytest test_presigned_upload.py::TestPresignedURLGeneration::test_presigned_url_generation
pytest test_shield_integration.py::TestShieldIntegration::test_clean_file_flow
```

## Test Scenarios

### 1. Presigned URL Generation
- ✅ Valid presigned URL structure
- ✅ Required metadata fields present
- ✅ Correct expiration time (5 minutes)
- ✅ SSM parameter retrieval
- ✅ DynamoDB status record creation
- ✅ Error handling for missing SSM parameter

### 2. Clean File Upload Flow
- ✅ Upload clean SVG to Shield bucket
- ✅ GuardDuty scan completion
- ✅ File movement to processing bucket
- ✅ Shield bucket cleanup
- ✅ Conversion process initiation
- ✅ Final PES file generation
- ✅ Download URL generation

### 3. Malware Detection (EICAR)
- ✅ Upload EICAR-wrapped SVG
- ✅ GuardDuty malware detection
- ✅ File rejection and deletion
- ✅ Status update to "infected"
- ✅ No processing bucket contamination
- ✅ Security event logging

### 4. Status Polling
- ✅ Status progression tracking
- ✅ Ready state with download URL
- ✅ Infected state with error message
- ✅ Processing states with progress messages
- ✅ Not found handling
- ✅ Error state handling

### 5. IAM Permissions
- ✅ Shield bucket read access
- ✅ Processing bucket write access
- ✅ DynamoDB table access
- ✅ Lambda invoke permissions
- ✅ SSM parameter read access

### 6. Cleanup Verification
- ✅ Shield bucket stays empty
- ✅ Processing bucket stays empty
- ✅ Only converted files in storage bucket
- ✅ DynamoDB TTL cleanup

## Test Data

### Clean Test SVG
Simple geometric pattern designed for embroidery conversion:
- 200x200 pixel canvas
- Basic shapes (rectangles, circles, lines)
- Text elements
- Pattern definitions
- Suitable for PES conversion

### EICAR Test SVG
EICAR test string embedded in SVG format:
- Multiple EICAR string placements
- Hidden text elements
- Comments and metadata
- Visual elements to appear legitimate
- Designed to trigger GuardDuty detection

## Monitoring and Debugging

### Test Logs
Tests use Python logging to provide detailed output:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### CloudWatch Logs
Integration tests will generate CloudWatch logs in:
- `/aws/lambda/urgd-stitch-upload-url-generator-dev`
- `/aws/lambda/urgd-stitch-status-checker-dev`
- `/aws/lambda/urgd-stitch-shield-callback-dev`

### Debug Mode
Run tests with debug output:
```bash
pytest -v -s --log-cli-level=DEBUG
```

## Continuous Integration

### GitHub Actions
Tests are automatically run in CI/CD pipeline:
- Unit tests run on every commit
- Integration tests run on dev deployments
- EICAR tests run in isolated environment

### Test Reports
Test results are published to:
- GitHub Actions summary
- CloudWatch test metrics
- S3 test artifacts bucket

## Troubleshooting

### Common Issues

1. **SSM Parameter Not Found**
   - Ensure Shield is deployed
   - Check parameter name: `/urgd/shield/quarantine_bucket_name`

2. **DynamoDB Table Not Found**
   - Ensure Stitch infrastructure is deployed
   - Check table name: `urgd-stitch-conversion-status-dev`

3. **S3 Bucket Access Denied**
   - Check IAM permissions
   - Verify bucket names and regions

4. **Lambda Invoke Failed**
   - Check Lambda function ARNs
   - Verify IAM invoke permissions

5. **Integration Test Timeout**
   - Check API endpoint availability
   - Verify GuardDuty is enabled
   - Check CloudWatch logs for errors

### Debug Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check SSM parameters
aws ssm get-parameter --name /urgd/shield/quarantine_bucket_name

# Check DynamoDB table
aws dynamodb describe-table --table-name urgd-stitch-conversion-status-dev

# Check S3 buckets
aws s3 ls s3://urgd-shield-quarantine-prod-*
aws s3 ls s3://urgd-stitch-processing-dev-*
aws s3 ls s3://urgd-stitch-storage-dev-*

# Check Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `stitch`)].FunctionName'
```

## Test Coverage

Current test coverage targets:
- ✅ Presigned URL generation: 100%
- ✅ Status checking: 100%
- ✅ Shield callback processing: 100%
- ✅ Error handling: 95%
- ✅ Integration flows: 90%

## Contributing

When adding new tests:

1. Follow naming convention: `test_*.py`
2. Use descriptive test names
3. Add appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
4. Include docstrings explaining test purpose
5. Update this README with new test scenarios
6. Ensure tests are deterministic and isolated
