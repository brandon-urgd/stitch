# Stitch Deployment Guide

## Quick Start

1. **Create GitHub Repository**
   ```bash
   # Create new repo on GitHub named "stitch"
   git clone https://github.com/yourusername/stitch.git
   cd stitch
   ```

2. **Set up GitHub Secrets**
   Go to your repository Settings > Secrets and variables > Actions, add:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `AWS_REGION`: us-east-1 (or your preferred region)
   - `AWS_ACCOUNT_ID`: Your AWS account ID

3. **Deploy**
   ```bash
   git add .
   git commit -m "Initial stitch deployment"
   git push origin main
   ```

4. **Access Your App**
   - Check the GitHub Actions workflow logs
   - The Function URL will be displayed in the workflow output
   - Open the URL in your browser to use the converter

## Manual Deployment (Alternative)

If you prefer to deploy manually:

1. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://urgd-stitch-storage --region us-east-1
   ```

2. **Build and Deploy Lambda**
   ```bash
   cd scripts
   ./build-layer.sh
   cd ..
   
   # Create Lambda function
   aws lambda create-function \
     --function-name urgd-stitch \
     --runtime python3.11 \
     --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
     --handler svg_converter.lambda_handler \
     --zip-file fileb://lambda/svg_converter.zip
   ```

3. **Create Function URL**
   ```bash
   aws lambda create-function-url-config \
     --function-name urgd-stitch \
     --auth-type NONE \
     --cors '{"AllowCredentials": false, "AllowHeaders": ["*"], "AllowMethods": ["*"], "AllowOrigins": ["*"]}'
   ```

## Testing

1. Open the Function URL in your browser
2. Upload a test SVG file (try the heart SVG from desktop)
3. Verify the PES file downloads correctly
4. Test with your embroidery machine

### Professional Quality Validation
The converter now includes professional embroidery standards:
- **6.3 SPI density** for smooth, even coverage
- **Intelligent stitch selection** (satin vs fill based on shape width)
- **Underlay stitches** for fabric stability
- **Quality control** with coordinate validation and length limits

### Test Files
- Use `test-heart.svg` from desktop for testing
- Expected output: `test-heart.pes` with professional quality
- Verify stitch density and pattern quality

## Troubleshooting

- **Function URL not working**: Check CORS configuration
- **Conversion fails**: Verify pyembroidery is installed in the layer
- **S3 errors**: Ensure Lambda has proper IAM permissions
- **Large files**: Increase Lambda timeout and memory if needed

## Cost Optimization

- S3 lifecycle policy deletes files after 24 hours
- Lambda only runs when converting files
- No persistent infrastructure costs
