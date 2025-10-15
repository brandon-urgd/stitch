import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Enhanced health check endpoint for stitch service.
    Returns detailed system status information.
    """
    try:
        s3_client = boto3.client('s3')
        bucket_name = os.environ.get('BUCKET_NAME')
        
        # Check S3 connectivity
        s3_healthy = False
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            s3_healthy = True
        except Exception as e:
            print(f"S3 health check failed: {e}")
        
        # Check pyembroidery availability
        pyembroidery_available = False
        try:
            import pyembroidery
            pyembroidery_available = True
        except ImportError:
            pass
        
        # Build health response
        health_data = {
            'status': 'healthy' if s3_healthy else 'degraded',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'environment': os.environ.get('ENVIRONMENT', 'unknown'),
            'region': os.environ.get('AWS_REGION', 'us-west-2'),
            'version': os.environ.get('VERSION', 'unknown'),
            'service': 'stitch',
            'checks': {
                's3_connectivity': 'healthy' if s3_healthy else 'unhealthy',
                'pyembroidery_layer': 'available' if pyembroidery_available else 'unavailable',
                'lambda_runtime': 'python3.12'
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(health_data)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        }
