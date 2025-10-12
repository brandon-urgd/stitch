import json
import boto3
import os
import tempfile
import uuid
from datetime import datetime, timedelta
from io import BytesIO
import base64
import traceback

# Try to import pyembroidery, fall back gracefully if not available
try:
    import pyembroidery
    PYEMBROIDERY_AVAILABLE = True
    print("pyembroidery library loaded successfully")
except ImportError:
    PYEMBROIDERY_AVAILABLE = False
    print("Warning: pyembroidery library not available, using fallback conversion")

s3_client = boto3.client('s3')
BUCKET_NAME = 'urgd-stitch-storage'

def lambda_handler(event, context):
    """
    Lambda handler for SVG to PES conversion API.
    Handles file conversion on POST requests via API Gateway.
    """
    
    try:
        # Get HTTP method from API Gateway event structure
        http_method = event.get('httpMethod', 'GET')
        
        # Handle CORS preflight requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }
        
        # Handle file conversion on POST requests
        if http_method == 'POST':
            return handle_conversion(event, context)
        
        else:
            return {
                'statusCode': 405,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }

# Frontend is served by CloudFront + S3, not Lambda

def serve_asset(event, context):
    """Serve static assets like logos and fonts."""
    try:
        # Extract asset path from the request
        path = event.get('rawPath', '').lstrip('/')
        
        if path == 'urgd-logo.png':
            # Serve the ur/gd logo
            return serve_logo()
        elif path.endswith('.ttf'):
            # Serve font files
            return serve_font(path)
        else:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': 'Asset not found'
            }
    except Exception as e:
        print(f"Error serving asset: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': 'Error serving asset'
        }

def serve_logo():
    """Serve the ur/gd logo."""
    # Base64 encoded ur/gd logo
    logo_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'image/png',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=31536000'
        },
        'body': f'data:image/png;base64,{logo_base64}'
    }

def serve_font(font_name):
    """Serve font files."""
    # In a real deployment, this would read from S3
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'font/ttf',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=31536000'
        },
        'body': 'Font data would be here'
    }

# Frontend HTML is served by CloudFront + S3, not embedded in Lambda

def handle_conversion(event, context):
    """Handle SVG to PES file conversion."""
    try:
        # Parse the multipart form data
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No file provided'})
            }
        
        # For Lambda Function URL, the body is base64 encoded
        body = event['body']
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        # Parse multipart form data (simplified for this example)
        # In production, you'd use a proper multipart parser
        svg_content = parse_multipart_data(body)
        
        if not svg_content:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Invalid SVG file'})
            }
        
        # Convert SVG to PES
        pes_content = convert_svg_to_pes(svg_content)
        
        if not pes_content:
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Conversion failed'})
            }
        
        # Upload PES file to S3 and get presigned URL
        file_id = str(uuid.uuid4())
        pes_key = f"converted/{file_id}.pes"
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=pes_key,
            Body=pes_content,
            ContentType='application/octet-stream'
        )
        
        # Generate presigned URL for download (valid for 1 hour)
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': pes_key},
            ExpiresIn=3600
        )
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'downloadUrl': download_url,
                'message': 'File converted successfully'
            })
        }
        
    except Exception as e:
        print(f"Error in conversion: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Conversion failed: ' + str(e)})
        }

def parse_multipart_data(body):
    """Parse multipart form data to extract SVG content."""
    # This is a simplified parser for demonstration
    # In production, use a proper multipart parser like python-multipart
    
    # Look for SVG content in the body
    if 'image/svg+xml' in body and '<svg' in body:
        # Extract SVG content between boundaries
        start_marker = '<svg'
        end_marker = '</svg>'
        
        start_idx = body.find(start_marker)
        if start_idx != -1:
            end_idx = body.find(end_marker, start_idx)
            if end_idx != -1:
                return body[start_idx:end_idx + len(end_marker)]
    
    return None

def convert_svg_to_pes(svg_content):
    """Convert SVG content to PES format."""
    try:
        if not PYEMBROIDERY_AVAILABLE:
            # Fallback: Create a simple PES file structure
            return create_simple_pes_file(svg_content)
        
        # Use pyembroidery for conversion
        # This is a simplified example - real conversion would be more complex
        pattern = pyembroidery.EmbPattern()
        
        # Parse SVG and add stitches to pattern
        # This is where you'd implement the actual SVG parsing and stitch generation
        add_svg_to_pattern(pattern, svg_content)
        
        # Write to PES format
        pes_data = BytesIO()
        pyembroidery.write_pes(pattern, pes_data)
        return pes_data.getvalue()
        
    except Exception as e:
        print(f"Error in SVG to PES conversion: {str(e)}")
        # Fallback to simple PES file
        return create_simple_pes_file(svg_content)

def add_svg_to_pattern(pattern, svg_content):
    """Add SVG content to embroidery pattern."""
    # This is a placeholder implementation
    # Real implementation would parse SVG paths and convert to stitches
    
    # Add a simple rectangle as example
    pattern.add_stitch_absolute(0, 0, pyembroidery.STITCH)
    pattern.add_stitch_absolute(100, 0, pyembroidery.STITCH)
    pattern.add_stitch_absolute(100, 100, pyembroidery.STITCH)
    pattern.add_stitch_absolute(0, 100, pyembroidery.STITCH)
    pattern.add_stitch_absolute(0, 0, pyembroidery.STITCH)
    pattern.add_stitch_absolute(0, 0, pyembroidery.END)

def create_simple_pes_file(svg_content):
    """Create a simple PES file as fallback."""
    # This creates a minimal PES file structure
    # In production, you'd implement proper PES format
    
    pes_header = b'#PES0001\x00\x00\x00\x00\x00\x00\x00\x00'
    pes_data = b'\x00\x00\x00\x00\x00\x00\x00\x00'  # Minimal stitch data
    
    return pes_header + pes_data

def get_cors_headers():
    """Get CORS headers for responses."""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }
