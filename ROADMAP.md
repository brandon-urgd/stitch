# Stitch - Multi-Format Conversion Roadmap

## Current Status ✅
- **SVG to PES conversion** - Live and working
- **Multi-format embroidery support** - PES, DST, EXP, JEF, HUS, VIP, VP3
- **Environment-aware API** - Dev/Prod deployments
- **High-quality settings** - Professional embroidery output
- **Scalable architecture** - Lambda + API Gateway + S3

## Future Multi-Format Conversion System 🚀

### Frontend Selector UI
```html
<!-- Input Selection -->
<select id="inputFormat">
  <option value="svg">SVG</option>
  <option value="png">PNG</option>
  <option value="jpg">JPG</option>
  <option value="ai">Adobe Illustrator</option>
  <option value="pdf">PDF</option>
</select>

<!-- Output Selection (dynamically populated) -->
<select id="outputFormat">
  <option value="pes">PES (Brother)</option>
  <option value="dst">DST (Tajima)</option>
  <option value="exp">EXP (Melco)</option>
  <option value="jef">JEF (Janome)</option>
  <option value="hus">HUS (Husqvarna)</option>
  <option value="vip">VIP (Pfaff)</option>
  <option value="vp3">VP3 (Pfaff)</option>
</select>
```

### API Gateway Routing
```
POST /convert/{inputFormat}/{outputFormat}
├── /convert/svg/pes → Lambda-SVG-Converter
├── /convert/svg/dst → Lambda-SVG-Converter  
├── /convert/png/pes → Lambda-Image-Converter
├── /convert/jpg/dst → Lambda-Image-Converter
├── /convert/ai/exp → Lambda-AI-Converter
└── /convert/pdf/jef → Lambda-PDF-Converter
```

### Lambda Function Architecture
```
urgd-converters/
├── svg-converter/     (current - handles all embroidery formats)
├── image-converter/   (PNG/JPG → embroidery)
├── ai-converter/      (Adobe Illustrator → embroidery)
├── pdf-converter/     (PDF → embroidery)
└── shared-layers/     (common dependencies)
```

### Dynamic Capability Detection
```javascript
// Frontend logic
const capabilities = {
  'svg': ['pes', 'dst', 'exp', 'jef', 'hus', 'vip', 'vp3'],
  'png': ['pes', 'dst', 'exp'],
  'jpg': ['pes', 'dst'],
  'ai': ['pes', 'dst', 'exp', 'jef'],
  'pdf': ['pes', 'dst', 'exp']
};

// Update output options based on input selection
function updateOutputOptions(inputFormat) {
  const outputSelect = document.getElementById('outputFormat');
  outputSelect.innerHTML = capabilities[inputFormat]
    .map(format => `<option value="${format}">${format.toUpperCase()}</option>`)
    .join('');
}
```

## Implementation Plan 📋

### Phase 1: Image Conversion
- [ ] Add PNG/JPG input support
- [ ] Create `image-converter` Lambda function
- [ ] Add image processing layer (Pillow + OpenCV)
- [ ] Update API Gateway routes

### Phase 2: Adobe Illustrator Support
- [ ] Add AI file input support
- [ ] Create `ai-converter` Lambda function
- [ ] Add AI file parsing capabilities
- [ ] Update frontend selector

### Phase 3: PDF Support
- [ ] Add PDF input support
- [ ] Create `pdf-converter` Lambda function
- [ ] Add PDF parsing and vector extraction
- [ ] Update API routing

### Phase 4: Advanced Features
- [ ] Batch conversion support
- [ ] Custom stitch pattern library
- [ ] Embroidery preview/simulation
- [ ] Quality analysis dashboard

## Current Foundation ✅

**What's Already Built:**
- ✅ **Multi-format output** - `pyembroidery` supports all major embroidery formats
- ✅ **Environment-aware API** - Easy to add new endpoints
- ✅ **Lambda layer system** - Can add new converters with shared dependencies
- ✅ **CloudFormation templates** - Easy to add new Lambda functions
- ✅ **CI/CD pipelines** - Automated deployment for new converters

**Ready for Expansion:**
- 🎯 **Scalable architecture** - Each converter gets its own Lambda function
- 🎯 **Shared dependencies** - Common layers for image processing
- 🎯 **Clean API design** - RESTful endpoints for each conversion type
- 🎯 **Frontend flexibility** - Dynamic UI based on available conversions

## Technical Notes 🔧

### Lambda Layer Strategy
- **`svg-embroidery`** - Current layer for SVG processing and embroidery generation
- **`image-processing`** - Future layer for PNG/JPG processing (Pillow + OpenCV)
- **`ai-processing`** - Future layer for Adobe Illustrator file parsing
- **`pdf-processing`** - Future layer for PDF vector extraction

### API Design
- **Consistent response format** across all converters
- **Error handling** standardized for all input types
- **Quality settings** configurable per conversion type
- **File validation** appropriate for each input format

### Frontend Architecture
- **Dynamic capability detection** - Show only available output formats
- **Progressive enhancement** - Graceful degradation for unsupported formats
- **Consistent UX** - Same interface regardless of input type
- **Real-time feedback** - Progress indicators and quality assessment

---

**The current SVG converter is just the beginning!** 🚀

*This roadmap outlines the path to a comprehensive multi-format embroidery conversion platform.*
