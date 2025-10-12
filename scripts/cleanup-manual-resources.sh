#!/bin/bash

# Clean up manually created AWS resources before CloudFormation deployment
set -e

echo "🧹 Cleaning up manually created resources..."

# Delete CloudFront distribution
echo "Deleting CloudFront distribution..."
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query 'DistributionList.Items[?Comment==`Stitch SVG to PES Converter - stitch.urgdstudios.com`].Id' --output text)
if [ -n "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
    echo "Found distribution: $DISTRIBUTION_ID"
    # Disable the distribution first
    aws cloudfront get-distribution-config --id "$DISTRIBUTION_ID" > /tmp/dist-config.json
    ETAG=$(jq -r '.ETag' /tmp/dist-config.json)
    jq '.DistributionConfig.Enabled = false' /tmp/dist-config.json > /tmp/dist-config-disabled.json
    aws cloudfront update-distribution --id "$DISTRIBUTION_ID" --distribution-config file:///tmp/dist-config-disabled.json --if-match "$ETAG"
    
    echo "Waiting for distribution to be disabled..."
    aws cloudfront wait distribution-deployed --id "$DISTRIBUTION_ID"
    
    # Delete the distribution
    aws cloudfront delete-distribution --id "$DISTRIBUTION_ID" --if-match "$ETAG"
    echo "✅ CloudFront distribution deleted"
else
    echo "No CloudFront distribution found"
fi

# Delete Lambda Function URL
echo "Deleting Lambda Function URL..."
aws lambda delete-function-url-config --function-name urgd-stitch 2>/dev/null || echo "No Function URL found"

# Delete Lambda function
echo "Deleting Lambda function..."
aws lambda delete-function --function-name urgd-stitch 2>/dev/null || echo "No Lambda function found"

# Delete Lambda layer
echo "Deleting Lambda layer..."
aws lambda delete-layer-version --layer-name urgd-stitch-libs --version-number 1 2>/dev/null || echo "No Lambda layer found"

# Delete IAM role
echo "Deleting IAM role..."
aws iam detach-role-policy --role-name lambda-execution-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null || true
aws iam delete-role-policy --role-name lambda-execution-role --policy-name S3Access 2>/dev/null || true
aws iam delete-role --role-name lambda-execution-role 2>/dev/null || echo "No IAM role found"

# Delete S3 bucket contents and bucket
echo "Deleting S3 bucket..."
aws s3 rm s3://urgd-stitch-storage --recursive 2>/dev/null || echo "No S3 bucket contents found"
aws s3 rb s3://urgd-stitch-storage 2>/dev/null || echo "No S3 bucket found"

# Delete Route 53 record
echo "Deleting Route 53 record..."
aws route53 change-resource-record-sets --hosted-zone-id Z0338626TGE7PTZDLIT1 --change-batch '{
  "Changes": [
    {
      "Action": "DELETE",
      "ResourceRecordSet": {
        "Name": "stitch.urgdstudios.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "db7920nbxuzs6.cloudfront.net"
          }
        ]
      }
    }
  ]
}' 2>/dev/null || echo "No Route 53 record found"

echo "✅ Cleanup completed! Ready for CloudFormation deployment."
