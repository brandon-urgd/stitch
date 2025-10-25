#!/usr/bin/env python3
"""
Register Stitch with Shield
This script is called during deployment to register Stitch's callback Lambda with Shield.
"""
import json
import os
import sys
import boto3

def main():
    # Get required environment variables
    callback_arn = os.environ.get('CALLBACK_ARN')
    shield_registration_arn = os.environ.get('SHIELD_REGISTRATION_ARN')
    
    if not callback_arn:
        print("❌ CALLBACK_ARN environment variable not set")
        sys.exit(1)
    
    if not shield_registration_arn:
        print("❌ SHIELD_REGISTRATION_ARN environment variable not set")
        sys.exit(1)
    
    try:
        # Create payload for Shield registration
        payload = {
            'action': 'register',
            'app_name': 'stitch',
            'callback_lambda_arn': callback_arn
        }
        
        print(f"🔍 Registering Stitch with Shield...")
        print(f"   Callback ARN: {callback_arn}")
        print(f"   Shield Registration ARN: {shield_registration_arn}")
        
        # Call Shield registration Lambda
        lambda_client = boto3.client('lambda', region_name='us-west-2')
        response = lambda_client.invoke(
            FunctionName=shield_registration_arn,
            Payload=json.dumps(payload)
        )
        
        # Parse response
        result = json.loads(response['Payload'].read())
        print(json.dumps(result, indent=2))
        
        # Check if registration was successful
        if result.get('body', {}).get('registration_successful'):
            print("✅ Shield registration successful")
            sys.exit(0)
        else:
            print("❌ Shield registration failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error during Shield registration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
