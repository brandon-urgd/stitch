# Stitch - SVG to PES Embroidery Converter

A lightweight web-based converter that transforms SVG files into PES embroidery format using AWS Lambda. Built by ur/gd with production-grade accuracy and reliability.

## Overview

Stitch provides a simple web interface for converting SVG files to PES format for embroidery machines. The entire conversion happens server-side, requiring only a web browser on the user's computer.

## Architecture

- **AWS Lambda Function** with Function URL (no API Gateway needed)
- **S3 Bucket** for temporary file storage
- **libpes/pyembroidery** for SVG to PES conversion
- **Embedded HTML/JS frontend** served directly from Lambda

## Usage

1. Open the Lambda Function URL in your browser
2. Click "Choose File" and select an SVG file
3. Click "Convert to PES"
4. Wait for conversion to complete
5. PES file automatically downloads

## Development

### Local Setup

```bash
# Install dependencies
pip install -r lambda/requirements.txt

# Test locally
python lambda/lambda_function.py
```

### Deployment

The repository uses GitHub Actions for automatic deployment:

1. Push to `main` branch
2. GitHub Actions builds and deploys to AWS
3. Function URL is output in the workflow logs

### Required GitHub Secrets

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (default: us-east-1)

## File Structure

```
stitch/
├── .github/workflows/deploy.yml    # GitHub Actions workflow
├── lambda/
│   ├── lambda_function.py          # Main Lambda handler
│   ├── requirements.txt            # Python dependencies
│   └── frontend.html               # Embedded HTML interface
├── scripts/
│   └── build-layer.sh              # Build Lambda layer locally
└── README.md
```

## AWS Resources

- **S3 Bucket**: `urgd-stitch-storage`
- **Lambda Function**: `urgd-stitch`
- **Lambda Layer**: `urgd-stitch-libs`

## ur/gd Branding

The application features ur/gd branding including:
- ur/gd logo prominently displayed
- Archivo and Rubik font families
- Consistent ur/gd visual identity
- "Powered by ur/gd" attribution

## Conversion Quality

The converter uses production-grade libraries to ensure accurate SVG to PES conversion:

- Handles complex SVG paths and shapes
- Maintains proper stitch density and patterns
- Supports various SVG units (px, mm, inches)
- Validates output PES files for embroidery machine compatibility
