#!/usr/bin/env python3
"""
PES File Analyzer - Analyze the structure and quality of PES embroidery files
"""

import struct
import sys

def analyze_pes_file(filename):
    """Analyze a PES file and extract key information"""
    print(f"Analyzing PES file: {filename}")
    print("=" * 50)
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    
    # Check PES header
    if data[:8] == b'#PES0060':
        print("✓ Valid PES file format detected")
    else:
        print("✗ Invalid PES file format")
        return
    
    # Extract basic info from header (simplified parsing)
    try:
        # PES header structure (simplified)
        version = data[8:12]
        hoops = struct.unpack('<H', data[12:14])[0]
        width = struct.unpack('<H', data[16:18])[0]
        height = struct.unpack('<H', data[18:20])[0]
        
        print(f"Hoops: {hoops}")
        print(f"Design dimensions: {width} x {height}")
        
        # Look for stitch data patterns
        stitch_count = 0
        stitch_data_start = None
        
        # Search for stitch data patterns
        for i in range(len(data) - 4):
            # Look for common stitch command patterns
            if data[i:i+2] == b'\x00\x00':  # End of stitch sequence
                if stitch_data_start is None:
                    stitch_data_start = i
                break
            elif data[i:i+2] in [b'\x00\x01', b'\x00\x02', b'\x00\x03']:  # Stitch commands
                stitch_count += 1
        
        print(f"Estimated stitch count: {stitch_count}")
        
        # Look for thread information
        thread_sections = data.count(b'Thread')
        print(f"Thread sections found: {thread_sections}")
        
        # Check for embroidery objects
        emb_objects = data.count(b'CEmbOne')
        print(f"Embroidery objects: {emb_objects}")
        
        # Look for sewing segments
        sew_segments = data.count(b'CSewSeg')
        print(f"Sewing segments: {sew_segments}")
        
        # Analyze stitch density and complexity
        if stitch_count > 0:
            density = stitch_count / (width * height) if width > 0 and height > 0 else 0
            print(f"Stitch density: {density:.4f} stitches per unit area")
            
            if stitch_count > 100:
                print("✓ High stitch count - complex design")
            elif stitch_count > 50:
                print("✓ Medium stitch count - moderate complexity")
            else:
                print("⚠ Low stitch count - simple design")
        
        # Check for quality indicators
        print("\nQuality Analysis:")
        print("-" * 20)
        
        if emb_objects > 0:
            print("✓ Contains embroidery objects")
        else:
            print("✗ No embroidery objects found")
            
        if sew_segments > 0:
            print("✓ Contains sewing segments")
        else:
            print("✗ No sewing segments found")
            
        if stitch_count > 50:
            print("✓ Sufficient stitch count for detailed work")
        else:
            print("⚠ Low stitch count - may be too simple")
            
        # Check if it's just a basic shape
        if stitch_count < 20 and emb_objects == 1:
            print("⚠ WARNING: This appears to be a very simple shape (possibly just a square)")
        else:
            print("✓ Design appears to have reasonable complexity")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_pes.py <pes_file>")
        sys.exit(1)
    
    analyze_pes_file(sys.argv[1])
