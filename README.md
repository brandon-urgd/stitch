# Stitch - SVG to PES Embroidery Converter

**🎉 PRODUCTION READY** - A production-ready web application that converts SVG files to PES embroidery format using AWS infrastructure with enterprise-grade security.

## 🌐 Live Website

**Visit: https://stitch.urgdstudios.com**

Simply upload an SVG file and get a perfectly formatted PES file for your embroidery machine!

## ✨ Features

- **Professional Quality** - Industry-standard 6.3 SPI stitch density
- **Intelligent Stitching** - Automatic satin vs fill stitch selection
- **Underlay Support** - Fabric stability with professional underlay stitches
- **Quality Control** - Comprehensive validation and error handling
- **Drag & Drop Interface** - Easy file upload with visual feedback
- **Real-time Conversion** - Server-side processing with progress indicators
- **Instant Download** - Get your PES file immediately after conversion
- **Mobile Friendly** - Responsive design works on all devices
- **ur/gd Branding** - Professional design with ur/gd visual identity
- **🛡️ Malware Protection** - Automatic virus scanning with AWS GuardDuty
- **🔒 Secure Uploads** - Direct-to-S3 uploads with presigned URLs
- **⚡ Fast Processing** - Event-driven architecture for optimal performance

## 🏗️ Architecture

- **Frontend**: CloudFront + S3 static website hosting
- **Backend**: AWS Lambda with pyembroidery library
- **API**: API Gateway for secure file processing
- **Storage**: S3 buckets for temporary files and converted outputs
- **Security**: Origin Access Control (OAC) for secure S3 access
- **🛡️ Shield Integration**: AWS GuardDuty malware scanning with EventBridge
- **🔒 Secure Uploads**: Presigned URL direct-to-S3 uploads
- **⚡ Event-Driven**: Async processing with real-time status updates

## 🛡️ Shield Integration

Stitch includes enterprise-grade malware protection through AWS GuardDuty integration:

### How It Works
1. **Secure Upload**: Files upload directly to Shield quarantine bucket via presigned URLs
2. **Automatic Scanning**: GuardDuty scans files for malware (30-90 seconds)
3. **Event Processing**: Clean files proceed to conversion, infected files are rejected
4. **Real-time Status**: Frontend polls for conversion status with progress updates
5. **Automatic Cleanup**: Files are removed from quarantine after processing

### Security Features
- **Zero-touch Malware**: Infected files never touch Lambda compute
- **Real-time Detection**: EICAR and other malware patterns detected instantly
- **Automatic Rejection**: Malware files deleted immediately after detection
- **Audit Trail**: All security events logged to CloudWatch
- **Compliance Ready**: SOC 2, GDPR, and HIPAA compatible

### API Endpoints
- `GET /v1/upload-url` - Generate presigned upload URL
- `GET /v1/status/{request_id}` - Check conversion status

For detailed integration documentation, see [ur gd Shield Integration Standard.md](../../urgd_library/standards/ur%20gd%20Shield%20Integration%20Standard.md).

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
├── lambdas/                    # Lambda deployment packages
│   └── lambda-prod-{commit}.zip
├── cloudformation/            # Infrastructure templates
│   └── stitch-infrastructure.yaml
└── website/                   # Static website files
    ├── index.html
    └── assets/
```

## 🛠️ Development

### Testing
The application is designed for production use with comprehensive end-to-end testing:

- **Live Website Testing**: Use the production website at https://stitch.urgdstudios.com
- **API Testing**: Test upload and status endpoints directly
- **Shield Integration**: Upload files to verify malware scanning works
- **Staging Environment**: Full user flow validation before production

### Adding New Formats
The architecture supports easy addition of new embroidery formats:

1. Update `lambdas/svg_converter.py` with new format support
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
├── lambdas/
│   ├── svg_converter.py             # Main conversion logic
│   ├── upload_url_generator.py      # Presigned URL generation
│   ├── status_checker.py            # Status polling endpoint
│   ├── shield_callback.py           # GuardDuty event processor
│   ├── health_check.py              # Health check endpoint
│   └── requirements.txt             # Python dependencies
├── layers/
│   └── svg-embroidery/              # Lambda layer for pyembroidery
│       └── requirements.txt
├── website/
│   ├── index.html                   # Frontend interface
│   └── assets/                      # Fonts, logos, etc.
├── scripts/
│   └── register-with-shield.py      # Shield registration script
├── ROADMAP.md                       # Development roadmap
└── README.md
```

## 🔧 AWS Resources

- **CloudFront Distribution**: Global CDN for fast website delivery
- **S3 Website Bucket**: Static website hosting
- **S3 Storage Bucket**: Converted PES file storage
- **S3 Processing Bucket**: Temporary storage for clean files
- **Lambda Functions**: 
  - SVG to PES conversion engine
  - Presigned URL generator
  - Status checker
  - Shield callback processor
  - Health check endpoint
- **API Gateway**: RESTful API for file processing
- **DynamoDB Table**: Conversion status tracking
- **EventBridge Rule**: GuardDuty event routing
- **GuardDuty**: Malware scanning service
- **IAM Roles**: Secure permissions for all services

## 🎨 ur/gd Branding

- **Logo**: Prominent ur/gd logo with custom styling
- **Typography**: Archivo Bold + Rubik Regular fonts
- **Colors**: Professional gradient design
- **Attribution**: "Powered by ur/gd studios" with link

## 🔒 Security & Quality

- **Professional Standards**: 6.3 SPI density, proper stitch lengths
- **Intelligent Processing**: Automatic stitch type selection based on shape width
- **Quality Validation**: Coordinate validation, length limits, memory management
- **Input Validation**: SVG file type verification
- **Error Handling**: Graceful failure with user feedback
- **File Cleanup**: Automatic temporary file deletion
- **CORS Support**: Proper cross-origin headers
- **HTTPS Only**: All traffic encrypted
- **🛡️ Malware Protection**: AWS GuardDuty real-time virus scanning
- **🔒 Secure Uploads**: Presigned URL direct-to-S3 uploads
- **⚡ Zero-touch Security**: Malware never touches application compute
- **📊 Audit Trail**: Complete security event logging
- **🔄 Automatic Cleanup**: Infected files deleted immediately

## 📊 Performance

- **Global CDN**: CloudFront edge locations worldwide
- **Serverless**: Pay-per-use Lambda scaling
- **Fast Conversion**: Optimized professional quality processing
- **Memory Efficient**: 2000 stitches per block limit
- **Efficient Storage**: Lifecycle policies for cleanup

## 🎯 Professional Quality Standards

- **Stitch Density**: 6.3 SPI (4mm row spacing) - Professional standard
- **Stitch Lengths**: Fill (1.5mm), Satin (2.0mm), Running (2.5mm)
- **Intelligent Selection**: Satin for shapes <8mm, Fill for shapes ≥8mm
- **Underlay Stitches**: Perpendicular underlay for fabric stability
- **Quality Control**: Max 4mm stitch length, min 0.5mm, coordinate validation
- **Memory Management**: 2000 stitches per block to prevent issues

## 🚀 Getting Started

### For Users
1. Visit https://stitch.urgdstudios.com
2. Upload your SVG file
3. Wait for conversion (usually 30-90 seconds)
4. Download your PES file

### For Developers
1. Clone the repository
2. Deploy to dev environment using GitHub Actions
3. Test with sample SVG files
4. Deploy to staging for full validation
5. Deploy to production when ready

### For Integration
1. Read the [Shield Integration Standard](../../urgd_library/standards/ur%20gd%20Shield%20Integration%20Standard.md)
2. Implement callback Lambda following the standard
3. Update your upload flow to use Shield
4. Test with EICAR files for malware detection

## 📈 Monitoring

### CloudWatch Metrics
- **Conversion Success Rate**: Track successful conversions
- **Processing Time**: Monitor conversion performance
- **Error Rates**: Track and alert on failures
- **Security Events**: Monitor malware detection

### Logs
- **Lambda Execution**: All function logs in CloudWatch
- **API Gateway**: Request/response logging
- **Shield Integration**: Security event logging
- **DynamoDB**: Status tracking and debugging

## 🔧 Troubleshooting

### Common Issues

1. **Upload Fails**: Check presigned URL generation and S3 permissions
2. **Conversion Stuck**: Check DynamoDB status and Lambda logs
3. **Download Link Missing**: Verify conversion completed successfully
4. **Malware Detected**: File was infected and properly rejected
5. **API Errors**: Check API Gateway deployment and Lambda permissions

### Debug Commands

```bash
# Check API Gateway status
aws apigateway get-rest-apis --query 'items[?name==`urgd-stitch-api-dev`]'

# Check Lambda function status
aws lambda list-functions --query 'Functions[?contains(FunctionName, `stitch`)]'

# Check DynamoDB table
aws dynamodb describe-table --table-name urgd-stitch-conversion-status-dev

# Check S3 buckets
aws s3 ls s3://urgd-stitch-storage-dev-*
aws s3 ls s3://urgd-stitch-processing-dev-*
```

## 📚 Documentation

- **Architecture**: [Stitch Architecture.md](../../urgd_library/application%20archetecture/Stitch%20Architecture.md)
- **Shield Integration**: [Shield Integration Standard.md](../../urgd_library/standards/ur%20gd%20Shield%20Integration%20Standard.md)
- **Build Plan**: [stitch Build Plan.md](../../urgd_library/buildplans/stitch%20Build%20Plan.md)
- **Handoff Notes**: [Handoff Notes.md](../../urgd_library/buildplans/Handoff%20Notes.md)

## 🎯 Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and improvements.

## Support

- **Documentation**: Check this README and linked documentation
- **Issues**: Report bugs and feature requests via GitHub
- **Operations**: Contact ur/gd operations team for infrastructure issues
- **Development**: Contact ur/gd development team for integration questions

## License

UNLICENSED - ur/gd studios internal use only

---

**Built quietly powerful, by ur/gd studios**

*Professional embroidery conversion made simple*