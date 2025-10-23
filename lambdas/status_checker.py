import boto3
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Check conversion status for a request_id.
    
    This endpoint allows the frontend to poll for conversion status
    and get download URLs when ready.
    """
    
    try:
        # Extract request_id from path parameters
        request_id = event['pathParameters']['request_id']
        logger.info(f"Checking status for request: {request_id}")
        
        # Get DynamoDB table name from environment
        table_name = os.environ['STATUS_TABLE_NAME']
        table = dynamodb.Table(table_name)
        
        # Query DynamoDB for status
        response = table.get_item(Key={'request_id': request_id})
        
        if 'Item' not in response:
            logger.warning(f"Request not found: {request_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'status': 'not_found',
                    'message': 'Request ID not found'
                })
            }
        
        item = response['Item']
        status = item['status']
        logger.info(f"Status for {request_id}: {status}")
        
        if status == 'converted':
            # Generate presigned download URL
            storage_bucket = os.environ['STITCH_STORAGE_BUCKET']
            pes_key = item['pes_key']
            
            download_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': storage_bucket,
                    'Key': pes_key
                },
                ExpiresIn=3600  # 1 hour
            )
            
            logger.info(f"Generated download URL for {request_id}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'status': 'ready',
                    'download_url': download_url,
                    'stitch_count': item.get('stitch_count', 0),
                    'quality': item.get('quality', 'unknown'),
                    'message': 'Conversion complete'
                })
            }
            
        elif status == 'infected':
            logger.warning(f"Infected file detected for request: {request_id}")
            return {
                'statusCode': 403,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'status': 'infected',
                    'message': 'File contained malware and was rejected',
                    'scan_result': item.get('scan_result', 'Unknown threat detected')
                })
            }
            
        elif status == 'failed':
            logger.error(f"Conversion failed for request: {request_id}")
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'status': 'failed',
                    'message': 'Conversion failed',
                    'error': item.get('error', 'Unknown error')
                })
            }
            
        else:
            # scanning, uploading, or converting
            status_messages = {
                'uploading': 'Uploading file for security scan...',
                'scanning': 'Scanning for malware...',
                'converting': 'Converting SVG to embroidery format...'
            }
            
            message = status_messages.get(status, 'Processing in progress')
            
            return {
                'statusCode': 202,  # Accepted - processing
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'status': status,
                    'message': message,
                    'timestamp': item.get('timestamp', 'Unknown')
                })
            }
        
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        logger.error(f"Event: {json.dumps(event, default=str)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Failed to check status',
                'message': str(e)
            })
        }
