# Stitch - SVG to PES Embroidery Converter

**🎉 LIVE SERVICE** - A production-ready web application that converts SVG files to PES embroidery format using AWS infrastructure.

## 🌐 Live Website

**Visit: https://d3mjr86znz3p8h.cloudfront.net**

Simply upload an SVG file and get a perfectly formatted PES file for your embroidery machine!

## ✨ Features

- **Drag & Drop Interface** - Easy file upload with visual feedback
- **Real-time Conversion** - Server-side processing with progress indicators
- **Production Quality** - Uses pyembroidery library for accurate conversions
- **Instant Download** - Get your PES file immediately after conversion
- **Mobile Friendly** - Responsive design works on all devices
- **ur/gd Branding** - Professional design with ur/gd visual identity

## 🏗️ Architecture

- **Frontend**: CloudFront + S3 static website hosting
- **Backend**: AWS Lambda with pyembroidery library
- **API**: API Gateway for secure file processing
- **Storage**: S3 buckets for temporary files and converted outputs
- **Security**: Origin Access Control (OAC) for secure S3 access

## 🚀 Deployment

The application uses a fully automated CI/CD pipeline:

1. **Code Push** → GitHub Actions triggers
2. **Lambda Build** → Dependencies installed and packaged
3. **S3 Upload** → Artifacts uploaded to versioned folders
4. **CloudFormation** → Infrastructure deployed/updated
5. **Website Update** → Static files deployed with dynamic API URLs

### S3 Structure
```
urgd-applicationdata/stitch/
├── lambda/                    # Lambda deployment packages
│   └── lambda-prod-{commit}.zip
├── cloudformation/            # Infrastructure templates
│   └── stitch-infrastructure.yaml
└── website/                   # Static website files
    ├── index.html
    └── assets/
```

## 🛠️ Development

### Local Testing
```bash
# Test Lambda function locally
cd lambda
pip install -r requirements.txt
python lambda_function.py

# Test with sample SVG
curl -X POST -F "file=@test-heart.svg" https://your-api-gateway-url/prod/api
```

### Adding New Formats
The architecture supports easy addition of new embroidery formats:

1. Update `lambda/lambda_function.py` with new format support
2. Modify `website/index.html` to include format selection
3. Push changes - automatic deployment handles the rest

**Supported by pyembroidery:**
- PES (Brother) ✅ *Currently implemented*
- DST (Tajima)
- EXP (Melco) 
- HUS (Husqvarna)
- JEF (Janome)
- VP3 (Husqvarna)
- XXX (Singer)

## 📁 Repository Structure

```
stitch/
├── .github/workflows/
│   └── deploy-cloudformation.yml    # CI/CD pipeline
├── cloudformation/
│   └── stitch-infrastructure.yaml   # AWS infrastructure
├── lambda/
│   ├── lambda_function.py           # Main conversion logic
│   └── requirements.txt             # Python dependencies
├── website/
│   ├── index.html                   # Frontend interface
│   └── assets/                      # Fonts, logos, etc.
├── scripts/
│   └── deploy-cloudformation.sh     # Deployment script
└── README.md
```

## 🔧 AWS Resources

- **CloudFront Distribution**: Global CDN for fast website delivery
- **S3 Website Bucket**: Static website hosting
- **S3 Storage Bucket**: Temporary file storage
- **Lambda Function**: SVG to PES conversion engine
- **API Gateway**: RESTful API for file processing
- **IAM Roles**: Secure permissions for all services

## 🎨 ur/gd Branding

- **Logo**: Prominent ur/gd logo with custom styling
- **Typography**: Archivo Bold + Rubik Regular fonts
- **Colors**: Professional gradient design
- **Attribution**: "Powered by ur/gd studios" with link

## 🔒 Security & Quality

- **Input Validation**: SVG file type verification
- **Error Handling**: Graceful failure with user feedback
- **File Cleanup**: Automatic temporary file deletion
- **CORS Support**: Proper cross-origin headers
- **HTTPS Only**: All traffic encrypted

## 📊 Performance

- **Global CDN**: CloudFront edge locations worldwide
- **Serverless**: Pay-per-use Lambda scaling
- **Fast Conversion**: Optimized pyembroidery processing
- **Efficient Storage**: Lifecycle policies for cleanup

---

**Built with ❤️ by ur/gd studios**

*Professional embroidery conversion made simple*