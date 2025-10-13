#!/usr/bin/env python3
"""
Generate CloudFormation template with all 21 individual Lambda layers!
"""

layers = [
    "pillow", "numpy", "opencv", "scipy", "svgpathtools", "svgpath",
    "pyembroidery", "multipart", "scikit-image", "imageio", "rawpy",
    "exifread", "pillow-heif", "scikit-learn", "numba", "joblib",
    "pandas", "matplotlib", "seaborn", "cairosvg", "svglib", "reportlab"
]

def generate_layer_resource(layer_name):
    return f"""  # {layer_name.title()} Lambda Layer
  {layer_name.title()}Layer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: !Sub 'urgd-{layer_name}-${{Environment}}'
      Description: "{layer_name.title()} - ${{Environment}}"
      Content:
        S3Bucket: 'urgd-applicationdata'
        S3Key: 'stitch/layers/{layer_name}.zip'
      CompatibleRuntimes:
        - python3.12
      CompatibleArchitectures:
        - x86_64
      LicenseInfo: "MIT"
      RetentionPolicy: Retain
"""

# Generate all layer resources
layer_resources = "\n".join([generate_layer_resource(layer) for layer in layers])

# Generate the layers list for the Lambda function
layers_list = "\n".join([f"        - !Ref {layer.title()}Layer" for layer in layers])

print("🔥 Generated CloudFormation layers!")
print("💪 21 individual Lambda layers ready!")
print("🚀 Copy the layer resources and layers list to your CloudFormation template!")

print("\n" + "="*80)
print("LAYER RESOURCES (add to CloudFormation template):")
print("="*80)
print(layer_resources)

print("\n" + "="*80)
print("LAMBDA FUNCTION LAYERS (replace in StitchSvgConverterFunction):")
print("="*80)
print("      Layers:")
print(layers_list)
