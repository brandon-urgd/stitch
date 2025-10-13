#!/usr/bin/env python3
"""
Generate the ultimate 21-layer Lambda workflow!
EVERY PACKAGE GETS ITS OWN LAYER!
"""

layers = [
    "pillow", "numpy", "opencv", "scipy", "svgpathtools", "svgpath",
    "pyembroidery", "multipart", "scikit-image", "imageio", "rawpy",
    "exifread", "pillow-heif", "scikit-learn", "numba", "joblib",
    "pandas", "matplotlib", "seaborn", "cairosvg", "svglib", "reportlab"
]

def generate_build_step(layer_name):
    return f"""    - name: Build {layer_name.title()} Layer
      run: |
        echo "🔥 Building {layer_name.title()} Layer..."
        
        # Create build directory
        mkdir -p {layer_name}-build
        cd {layer_name}-build
        
        # Copy requirements
        cp ../layers/{layer_name}/requirements.txt .
        
        # Install Python dependencies
        pip install --upgrade pip setuptools wheel
        echo "⚡ Installing {layer_name} dependencies..."
        pip install -r requirements.txt -t ./python/ --no-cache-dir
        
        # Create the layer zip
        echo "💥 Creating {layer_name} layer package..."
        zip -r {layer_name}.zip python/
        
        # Get the size
        LAYER_SIZE=$(du -h {layer_name}.zip | cut -f1)
        echo "🎯 {layer_name.upper()} LAYER BUILT! Size: $LAYER_SIZE"
        
        # Upload to S3
        aws s3 cp {layer_name}.zip s3://urgd-applicationdata/stitch/layers/{layer_name}.zip --region us-west-2
        
        echo "🚀 {layer_name.upper()} LAYER DEPLOYED TO S3!"
"""

def generate_publish_step(layer_name):
    return f"""    - name: Publish {layer_name.title()} Layer
      run: |
        # Create {layer_name.title()} layer
        {layer_name.upper()}_LAYER_ARN=$(aws lambda publish-layer-version \\
          --layer-name urgd-{layer_name}-${{{{ github.event.inputs.environment }}}} \\
          --description "{layer_name.title()} - ${{{{ github.event.inputs.environment }}}}" \\
          --content S3Bucket=urgd-applicationdata,S3Key=stitch/layers/{layer_name}.zip \\
          --compatible-runtimes python3.12 \\
          --compatible-architectures x86_64 \\
          --query 'LayerVersionArn' \\
          --output text \\
          --region us-west-2)
        
        echo "🎯 {layer_name.title()} Layer ARN: ${layer_name.upper()}_LAYER_ARN"
        echo "{layer_name.upper()}_LAYER_ARN=${layer_name.upper()}_LAYER_ARN" >> $GITHUB_ENV
"""

# Generate the workflow
workflow = f"""name: Build Ultimate 21-Layer Lambda Arsenal

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment (dev/staging/prod)'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
          - prod

jobs:
  build-ultimate-layers:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
          aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
          aws-region: us-west-2

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \\
            build-essential \\
            libjpeg-dev \\
            libpng-dev \\
            libtiff-dev \\
            libfreetype6-dev \\
            liblcms2-dev \\
            libwebp-dev \\
            libharfbuzz-dev \\
            libfribidi-dev \\
            libxcb1-dev \\
            libffi-dev \\
            libssl-dev \\
            zlib1g-dev \\
            libbz2-dev \\
            libreadline-dev \\
            libsqlite3-dev \\
            libncursesw5-dev \\
            xz-utils \\
            tk-dev \\
            libxml2-dev \\
            libxmlsec1-dev \\
            libffi-dev \\
            liblzma-dev \\
            libopenblas-dev \\
            liblapack-dev \\
            gfortran \\
            libhdf5-dev \\
            pkg-config \\
            cmake \\
            libgtk-3-dev \\
            libavcodec-dev \\
            libavformat-dev \\
            libswscale-dev \\
            libv4l-dev \\
            libxvidcore-dev \\
            libx264-dev \\
            libjpeg-dev \\
            libpng-dev \\
            libtiff-dev \\
            libatlas-base-dev \\
            gfortran \\
            wget \\
            unzip

{chr(10).join([generate_build_step(layer) for layer in layers])}

{chr(10).join([generate_publish_step(layer) for layer in layers])}

    - name: Output Layer Info
      run: |
        echo "🚀 ALL 21 LAMBDA LAYERS DEPLOYED!"
        echo "💪 The ultimate Python arsenal is ready!"
        echo "🔥 Each package gets its own layer - maximum modularity!"
        echo "⚡ Ready to power your Lambda functions!"
        echo ""
        echo "📝 Layer ARNs:"
{chr(10).join([f'        echo "  - ${{{layer.upper()}_LAYER_ARN}}"' for layer in layers])}
"""

# Write the workflow
with open('/Users/brandon/Documents/Projects/urgd/stitch/.github/workflows/build-ultimate-21-layers.yml', 'w') as f:
    f.write(workflow)

print("🔥 Generated the ultimate 21-layer workflow!")
print("💪 EVERY PACKAGE GETS ITS OWN LAYER!")
print("🚀 Ready to build the most modular Lambda arsenal ever!")
