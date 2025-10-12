#!/bin/bash

# Deploy Stitch infrastructure using CloudFormation
set -e

ENVIRONMENT=${1:-dev}
STACK_NAME="urgd-stitch-${ENVIRONMENT}"
TEMPLATE_FILE="cloudformation/stitch-infrastructure.yaml"
REGION="${AWS_REGION:-us-west-2}"

# Get current git commit hash
GIT_COMMIT=$(git rev-parse --short HEAD)
echo "📦 Git commit: $GIT_COMMIT"

echo "🚀 Deploying Stitch infrastructure with CloudFormation..."

# Check if stack exists
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "📝 Updating existing CloudFormation stack..."
    if aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://"$TEMPLATE_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --parameters ParameterKey=Environment,ParameterValue="$ENVIRONMENT" ParameterKey=GitCommit,ParameterValue="$GIT_COMMIT" 2>&1 | tee /tmp/update-output.log; then
        echo "✅ Stack update initiated"
        echo "⏳ Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
    else
        # Check if the error is "No updates are to be performed"
        if grep -q "No updates are to be performed" /tmp/update-output.log; then
            echo "✅ Stack is already up to date - no changes needed"
        else
            echo "❌ Stack update failed"
            cat /tmp/update-output.log
            exit 1
        fi
    fi
else
    echo "🆕 Creating new CloudFormation stack..."
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://"$TEMPLATE_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --parameters ParameterKey=Environment,ParameterValue="$ENVIRONMENT" ParameterKey=GitCommit,ParameterValue="$GIT_COMMIT"
    
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
