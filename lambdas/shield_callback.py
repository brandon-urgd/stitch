import boto3
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')

# Environment variables
SHIELD_BUCKET = os.environ['SHIELD_BUCKET_NAME']
PROCESSING_BUCKET = os.environ['STITCH_PROCESSING_BUCKET']
CONVERTER_LAMBDA = os.environ['CONVERTER_LAMBDA_ARN']
STATUS_TABLE = os.environ['STATUS_TABLE_NAME']

def lambda_handler(event, context):
    """
    Process GuardDuty scan results for Stitch files.
    
    This Lambda is triggered by EventBridge when GuardDuty completes
    a malware scan on files in the Shield quarantine bucket.
    """
    
    try:
        # Enhanced logging for debugging
        logger.info("=" * 80)
        logger.info("SHIELD CALLBACK LAMBDA TRIGGERED")
        logger.info("=" * 80)
        logger.info(f"Full event structure: {json.dumps(event, default=str, indent=2)}")
        logger.info(f"Event keys: {list(event.keys())}")
        
        # Parse S3 Object Tagging event structure
        # S3 Object Tagging events have this structure:
        # {
        #   "detail": {
        #     "bucket": {
        #       "name": "bucket-name"
        #     },
        #     "object": {
        #       "key": "object/key"
        #     },
        #     "tags": {
        #       "GuardDutyMalwareScanStatus": "NO_THREATS_FOUND" or "THREATS_FOUND"
        #     }
        #   }
        # }
        
        detail = event.get('detail', {})
        logger.info(f"Detail section: {json.dumps(detail, default=str, indent=2)}")
        
        # Extract file information from S3 Object Tagging event
        bucket_name = detail.get('bucket', {}).get('name', '')
        object_key = detail.get('object', {}).get('key', '')
        event_tags = detail.get('tags', {})
        
        logger.info(f"Parsed - Bucket: {bucket_name}, Key: {object_key}")
        logger.info(f"Event tags: {event_tags}")
        
        if not bucket_name or not object_key:
            logger.error("Missing bucket name or object key in event")
            return {'statusCode': 400, 'body': 'Missing S3 details'}
        
        # Get object tags to determine scan status (more reliable than event tags)
        try:
            tags_response = s3_client.get_object_tagging(
                Bucket=bucket_name,
                Key=object_key
            )
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagSet', [])}
            scan_status = tags.get('GuardDutyMalwareScanStatus', 'UNKNOWN')
            logger.info(f"Object tags: {tags}")
            logger.info(f"Scan status from tags: {scan_status}")
        except Exception as e:
            logger.error(f"Failed to get object tags: {str(e)}")
            # Fallback to event tags if available
            scan_status = event_tags.get('GuardDutyMalwareScanStatus', 'UNKNOWN')
            logger.info(f"Using event tags fallback - scan status: {scan_status}")
        
        # Get metadata from S3 object
        try:
            metadata_response = s3_client.head_object(
                Bucket=bucket_name,
                Key=object_key
            )
            metadata = metadata_response.get('Metadata', {})
            logger.info(f"Object metadata: {metadata}")
        except Exception as e:
            logger.error(f"Failed to get object metadata: {str(e)}")
            return {'statusCode': 500, 'body': 'Failed to get object metadata'}
        
        # Filter by app-name (security isolation)
        app_name = metadata.get('app-name', '')
        if app_name != 'stitch':
            logger.info(f"Ignoring event for app: {app_name}")
            return {'statusCode': 200, 'body': 'Not for stitch'}
        
        # Extract request ID from S3 key (format: stitch/{request_id}/upload.svg)
        if not object_key.startswith('stitch/'):
            logger.error(f"Invalid S3 key format: {object_key}")
            return {'statusCode': 400, 'body': 'Invalid S3 key format'}
        
        try:
            request_id = object_key.split('/')[1]  # Extract from stitch/{request_id}/upload.svg
        except IndexError:
            logger.error(f"Could not extract request ID from S3 key: {object_key}")
            return {'statusCode': 400, 'body': 'Could not extract request ID'}
        
        logger.info(f"Processing request: {request_id}")
        
        # Get DynamoDB table
        table = dynamodb.Table(STATUS_TABLE)
        
        # Get request details from DynamoDB
        try:
            response = table.get_item(Key={'request_id': request_id})
            if 'Item' not in response:
                logger.error(f"Request not found in DynamoDB: {request_id}")
                return {'statusCode': 404, 'body': 'Request not found'}
            
            item = response['Item']
            destination_bucket = item.get('destination_bucket', PROCESSING_BUCKET)
            logger.info(f"Found destination bucket: {destination_bucket}")
        except Exception as e:
            logger.error(f"Failed to get request from DynamoDB: {str(e)}")
            return {'statusCode': 500, 'body': 'Failed to get request details'}
        
        if scan_status == 'NO_THREATS_FOUND':
            logger.info(f"Clean file detected: {object_key}")
            
            # Update status to converting
            try:
                table.update_item(
                    Key={'request_id': request_id},
                    UpdateExpression='SET #status = :status, #timestamp = :timestamp',
                    ExpressionAttributeNames={
                        '#status': 'status',
                        '#timestamp': 'timestamp'
                    },
                    ExpressionAttributeValues={
                        ':status': 'converting',
                        ':timestamp': timestamp
                    }
                )
                logger.info(f"Updated status to converting for request: {request_id}")
            except Exception as e:
                logger.error(f"Failed to update status: {str(e)}")
                return {'statusCode': 500, 'body': 'Failed to update status'}
            
            # Move file to processing bucket
            try:
                copy_source = {'Bucket': bucket_name, 'Key': object_key}
                processing_key = f"processing/{request_id}/upload.svg"
                
                s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=destination_bucket,
                    Key=processing_key,
                    Metadata=metadata,
                    MetadataDirective='REPLACE'
                )
                
                logger.info(f"File moved to processing bucket: {processing_key}")
            except Exception as e:
                logger.error(f"Failed to move file to processing bucket: {str(e)}")
                # Update status to failed
                table.update_item(
                    Key={'request_id': request_id},
                    UpdateExpression='SET #status = :status, #error = :error',
                    ExpressionAttributeNames={
                        '#status': 'status',
                        '#error': 'error'
                    },
                    ExpressionAttributeValues={
                        ':status': 'failed',
                        ':error': f'Failed to move to processing bucket: {str(e)}'
                    }
                )
                return {'statusCode': 500, 'body': 'Failed to move file'}
            
            # Delete from Shield quarantine
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=object_key)
                logger.info(f"File deleted from Shield: {object_key}")
            except Exception as e:
                logger.warning(f"Failed to delete from Shield (non-critical): {str(e)}")
            
            # Invoke converter Lambda
            try:
                lambda_client.invoke(
                    FunctionName=CONVERTER_LAMBDA,
                    InvocationType='Event',  # Async invocation
                    Payload=json.dumps({
                        'request_id': request_id,
                        'source_bucket': destination_bucket,
                        'source_key': processing_key
                    })
                )
                
                logger.info(f"Converter Lambda invoked for request: {request_id}")
            except Exception as e:
                logger.error(f"Failed to invoke converter Lambda: {str(e)}")
                # Update status to failed
                table.update_item(
                    Key={'request_id': request_id},
                    UpdateExpression='SET #status = :status, #error = :error',
                    ExpressionAttributeNames={
                        '#status': 'status',
                        '#error': 'error'
                    },
                    ExpressionAttributeValues={
                        ':status': 'failed',
                        ':error': f'Failed to invoke converter: {str(e)}'
                    }
                )
                return {'statusCode': 500, 'body': 'Failed to invoke converter'}
            
        else:
            # Infected file or other threat
            logger.warning(f"Infected file detected: {object_key}")
            logger.warning(f"Scan status: {scan_status}")
            
            # Get threat details if available
            threat_name = detail.get('service', {}).get('additionalInfo', {}).get('threatName', 'Unknown threat')
            
            # Update status to infected
            try:
                table.put_item(
                    Item={
                        'request_id': request_id,
                        'status': 'infected',
                        'scan_result': json.dumps({
                            'scanStatus': scan_status,
                            'threatName': threat_name,
                            'severity': detail.get('severity', 0)
                        }),
                        'timestamp': timestamp,
                        'ttl': int((context.aws_request_id and int(context.aws_request_id, 16) or 0) + (7 * 24 * 60 * 60))  # 7 days TTL
                    }
                )
                logger.info(f"Updated status to infected for request: {request_id}")
            except Exception as e:
                logger.error(f"Failed to update status to infected: {str(e)}")
            
            # Delete from Shield quarantine
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=object_key)
                logger.info(f"Infected file deleted from Shield: {object_key}")
            except Exception as e:
                logger.warning(f"Failed to delete infected file (non-critical): {str(e)}")
            
            # Log security event to CloudWatch
            logger.error(json.dumps({
                'event': 'malware_detected',
                'app': 'stitch',
                'request_id': request_id,
                'object_key': object_key,
                'scan_status': scan_status,
                'threat_name': threat_name,
                'timestamp': timestamp
            }))
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processed successfully'})
        }
        
    except Exception as e:
        logger.error(f"Error processing scan result: {str(e)}")
        logger.error(f"Event: {json.dumps(event, default=str)}")
        
        # Try to update status to failed if we have a request_id
        try:
            if 'request_id' in locals() and request_id:
                table = dynamodb.Table(STATUS_TABLE)
                table.update_item(
                    Key={'request_id': request_id},
                    UpdateExpression='SET #status = :status, #error = :error',
                    ExpressionAttributeNames={
                        '#status': 'status',
                        '#error': 'error'
                    },
                    ExpressionAttributeValues={
                        ':status': 'failed',
                        ':error': f'Callback processing error: {str(e)}'
                    }
                )
        except:
            pass  # Don't fail on status update
        
        raise
