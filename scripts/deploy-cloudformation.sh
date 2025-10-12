#!/bin/bash

# Deploy Stitch infrastructure using CloudFormation
set -e

STACK_NAME="stitch-infrastructure"
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
        --parameters ParameterKey=DomainName,ParameterValue="urgdstudios.com" \
                   ParameterKey=Subdomain,ParameterValue="stitch" \
                   ParameterKey=CertificateArn,ParameterValue="arn:aws:acm:us-east-1:198919428218:certificate/90d330b3-ad6c-4b24-9a9e-9188ededc595"
    
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
        --parameters ParameterKey=DomainName,ParameterValue="urgdstudios.com" \
                   ParameterKey=Subdomain,ParameterValue="stitch" \
                   ParameterKey=CertificateArn,ParameterValue="arn:aws:acm:us-east-1:198919428218:certificate/90d330b3-ad6c-4b24-9a9e-9188ededc595"
    
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

# Get the custom domain URL
CUSTOM_DOMAIN=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`CustomDomainUrl`].OutputValue' \
    --output text)

if [ "$CUSTOM_DOMAIN" != "None" ] && [ -n "$CUSTOM_DOMAIN" ]; then
    echo "🌐 Custom domain: $CUSTOM_DOMAIN"
    echo "⏳ Note: DNS propagation may take a few minutes..."
else
    FUNCTION_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`FunctionUrl`].OutputValue' \
        --output text)
    echo "🔗 Function URL: $FUNCTION_URL"
fi
