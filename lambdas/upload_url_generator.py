import boto3
import json
import os
import uuid
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
ssm_client = boto3.client('ssm')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Generate presigned URL for Shield bucket upload.
    
    This endpoint allows the frontend to upload files directly to Shield S3 bucket
    for malware scanning without touching Lambda compute.
    """
    
    try:
        logger.info("Generating presigned URL for Shield upload")
        
        # Get Shield bucket from SSM Parameter Store
        shield_bucket = ssm_client.get_parameter(
            Name='/urgd/shield/quarantine_bucket_name'
        )['Parameter']['Value']
        
        logger.info(f"Shield bucket: {shield_bucket}")
        
        # Get Stitch processing bucket from environment
        stitch_processing_bucket = os.environ['STITCH_PROCESSING_BUCKET']
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # S3 key with app prefix and request ID for callback identification
        s3_key = f"stitch/{request_id}/upload.svg"
        
        logger.info(f"Generated request ID: {request_id}")
        logger.info(f"S3 key: {s3_key}")
        
        # Create initial status record in DynamoDB
        status_table_name = os.environ['STATUS_TABLE_NAME']
        table = dynamodb.Table(status_table_name)
        
        table.put_item(
            Item={
                'request_id': request_id,
                'status': 'uploading',
                'timestamp': datetime.utcnow().isoformat(),
                'destination_bucket': stitch_processing_bucket,
                's3_key': s3_key,
                'ttl': int((datetime.utcnow().timestamp() + (7 * 24 * 60 * 60)))  # 7 days TTL
            }
        )
        
        logger.info(f"Created initial status record for request: {request_id}")
        
        # Generate presigned POST (more secure than presigned PUT)
        # POST allows us to set conditions and required fields
        # Note: Shield bucket policy only allows x-amz-meta-app-name metadata
        presigned_post = s3_client.generate_presigned_post(
            Bucket=shield_bucket,
            Key=s3_key,
            Fields={
                'x-amz-meta-app-name': 'stitch',
                'Content-Type': 'image/svg+xml'
            },
            Conditions=[
                {'x-amz-meta-app-name': 'stitch'},
                ['content-length-range', 1, 10485760],  # 1 byte to 10MB
                ['starts-with', '$Content-Type', 'image/']  # Only images
            ],
            ExpiresIn=300  # 5 minutes
        )
        
        logger.info(f"Generated presigned POST URL for request: {request_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'upload_url': presigned_post['url'],
                'fields': presigned_post['fields'],
                'request_id': request_id,
                'destination_bucket': stitch_processing_bucket,
                'upload_timestamp': datetime.utcnow().isoformat(),
                'expires_in': 300,
                'message': 'Upload directly to this URL using the provided fields'
            })
        }
        
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        logger.error(f"Event: {json.dumps(event, default=str)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Failed to generate upload URL',
                'message': str(e)
            })
        }

