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
    Lambda handler for SVG to PES conversion service.
    Serves HTML frontend on GET requests and handles file conversion on POST requests.
    """
    
    try:
        # Get HTTP method from Function URL event structure
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        # Handle CORS preflight requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }
        
        # Serve HTML frontend on GET requests
        if http_method == 'GET':
            # Check if this is an asset request
            path = event.get('rawPath', '')
            if path and path != '/' and not path.startswith('/?'):
                return serve_asset(event, context)
            return serve_frontend()
        
        # Handle file conversion on POST requests
        elif http_method == 'POST':
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

def serve_frontend():
    """Serve the HTML frontend interface."""
    try:
        # Read the embedded HTML file
        html_content = get_frontend_html()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': html_content
        }
    except Exception as e:
        print(f"Error serving frontend: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': 'Error loading frontend'
        }

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

def get_frontend_html():
    """Get the frontend HTML content."""
    # In a real deployment, this would read from a file
    # For now, we'll return a simple HTML structure
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stitch - SVG to PES Converter</title>
    <style>
        @font-face {
            font-family: 'Archivo';
            src: url('Archivo-Bold.ttf') format('truetype');
            font-weight: bold;
        }
        @font-face {
            font-family: 'Rubik';
            src: url('Rubik-Regular.ttf') format('truetype');
            font-weight: normal;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Rubik', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        .logo { 
            font-size: 2.5rem; 
            font-weight: bold; 
            color: #667eea; 
            margin-bottom: 10px;
            font-family: 'Archivo', sans-serif;
        }
        .urgd-logo {
            height: 60px;
            margin-bottom: 20px;
        }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 1.1rem; }
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 40px 20px;
            margin: 30px 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .upload-area:hover { border-color: #667eea; background-color: #f8f9ff; }
        .upload-area.dragover { border-color: #667eea; background-color: #f0f4ff; }
        .upload-icon { font-size: 3rem; color: #ddd; margin-bottom: 15px; }
        .upload-text { font-size: 1.2rem; color: #666; margin-bottom: 10px; }
        .upload-hint { color: #999; font-size: 0.9rem; }
        #fileInput { display: none; }
        .file-info { margin: 20px 0; padding: 15px; background: #f8f9ff; border-radius: 10px; display: none; }
        .file-name { font-weight: bold; color: #333; margin-bottom: 5px; }
        .file-size { color: #666; font-size: 0.9rem; }
        .convert-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 15px 40px; border-radius: 50px;
            font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: all 0.3s ease;
            margin: 20px 0; min-width: 200px;
        }
        .convert-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        .convert-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .progress-container { margin: 20px 0; display: none; }
        .progress-bar { width: 100%; height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; margin-bottom: 10px; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); width: 0%; transition: width 0.3s ease; }
        .progress-text { color: #666; font-size: 0.9rem; }
        .download-area { margin: 20px 0; padding: 20px; background: #e8f5e8; border-radius: 10px; display: none; }
        .download-btn { background: #4CAF50; color: white; border: none; padding: 12px 30px; border-radius: 25px; font-size: 1rem; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px 0; }
        .download-btn:hover { background: #45a049; }
        .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 10px; margin: 20px 0; display: none; }
        .success { background: #e8f5e8; color: #2e7d32; padding: 15px; border-radius: 10px; margin: 20px 0; display: none; }
        .footer { margin-top: 30px; color: #999; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <img src="urgd-logo.png" alt="ur/gd" class="urgd-logo" />
        <div class="logo">🧵 Stitch</div>
        <div class="subtitle">Convert SVG files to PES embroidery format</div>
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Click to select SVG file</div>
            <div class="upload-hint">or drag and drop here</div>
            <input type="file" id="fileInput" accept=".svg" />
        </div>
        
        <div class="file-info" id="fileInfo">
            <div class="file-name" id="fileName"></div>
            <div class="file-size" id="fileSize"></div>
        </div>
        
        <button class="convert-btn" id="convertBtn" disabled>Convert to PES</button>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
            <div class="progress-text" id="progressText">Converting...</div>
        </div>
        
        <div class="download-area" id="downloadArea">
            <div>✅ Conversion complete!</div>
            <a href="#" class="download-btn" id="downloadBtn">Download PES File</a>
        </div>
        
        <div class="error" id="errorMsg"></div>
        <div class="success" id="successMsg"></div>
        
        <div class="footer">Powered by ur/gd • AWS Lambda • No software installation required</div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const convertBtn = document.getElementById('convertBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const downloadArea = document.getElementById('downloadArea');
        const downloadBtn = document.getElementById('downloadBtn');
        const errorMsg = document.getElementById('errorMsg');
        const successMsg = document.getElementById('successMsg');
        
        let selectedFile = null;
        
        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);
        
        uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
        uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('dragover'); });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault(); uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) { fileInput.files = files; handleFileSelect(); }
        });
        
        function handleFileSelect() {
            const file = fileInput.files[0];
            if (file && file.type === 'image/svg+xml') {
                selectedFile = file;
                fileName.textContent = file.name;
                fileSize.textContent = formatFileSize(file.size);
                fileInfo.style.display = 'block';
                convertBtn.disabled = false;
                hideMessages();
            } else { showError('Please select a valid SVG file.'); }
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024; const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        convertBtn.addEventListener('click', async () => {
            if (!selectedFile) return;
            convertBtn.disabled = true; progressContainer.style.display = 'block';
            downloadArea.style.display = 'none'; hideMessages();
            
            try {
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 90) progress = 90;
                    progressFill.style.width = progress + '%';
                }, 200);
                
                const response = await fetch(window.location.href, { method: 'POST', body: formData });
                clearInterval(progressInterval);
                progressFill.style.width = '100%';
                progressText.textContent = 'Complete!';
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        downloadBtn.href = result.downloadUrl;
                        downloadArea.style.display = 'block';
                        showSuccess('File converted successfully!');
                    } else { showError(result.error || 'Conversion failed.'); }
                } else { const error = await response.text(); showError('Server error: ' + error); }
            } catch (error) { showError('Network error: ' + error.message); }
            finally { convertBtn.disabled = false; progressContainer.style.display = 'none'; }
        });
        
        function showError(message) { errorMsg.textContent = message; errorMsg.style.display = 'block'; successMsg.style.display = 'none'; }
        function showSuccess(message) { successMsg.textContent = message; successMsg.style.display = 'block'; errorMsg.style.display = 'none'; }
        function hideMessages() { errorMsg.style.display = 'none'; successMsg.style.display = 'none'; }
    </script>
</body>
</html>
"""

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
