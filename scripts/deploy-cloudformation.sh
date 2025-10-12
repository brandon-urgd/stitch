#!/bin/bash

# Deploy Stitch infrastructure using CloudFormation
set -e

STACK_NAME="urgd-stitch-infrastructure"
TEMPLATE_FILE="cloudformation/stitch-infrastructure.yaml"
REGION="${AWS_REGION:-us-west-2}"

echo "🚀 Deploying Stitch infrastructure with CloudFormation..."

# Check if stack exists
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "📝 Updating existing CloudFormation stack..."
    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --parameters ParameterKey=Environment,ParameterValue="prod"
    
    echo "⏳ Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"
else
    echo "🆕 Creating new CloudFormation stack..."
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --parameters ParameterKey=Environment,ParameterValue="prod"
    
    echo "⏳ Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"
fi

echo "✅ CloudFormation deployment completed!"

# Get outputs
echo "📋 Stack outputs:"
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs' \
    --output table

# Get the CloudFront URL
CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
    --output text)

if [ "$CLOUDFRONT_URL" != "None" ] && [ -n "$CLOUDFRONT_URL" ]; then
    echo "☁️  CloudFront URL: $CLOUDFRONT_URL"
    echo "⏳ Note: CloudFront distribution may take a few minutes to propagate..."
else
    echo "❌ CloudFront URL not found in stack outputs"
fi
