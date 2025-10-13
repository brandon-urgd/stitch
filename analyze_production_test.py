#!/usr/bin/env python3
"""
Analyze the production Nicole Project PES file results
"""

import struct
import json

def analyze_pes_file(filename, label):
    """Analyze a PES file and return detailed information."""
    print(f"\n=== {label} ===")
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"File: {filename}")
    print(f"Size: {len(data)} bytes")
    
    # Check PES header
    if not data.startswith(b'#PES'):
        print("❌ Invalid PES file")
        return None
    
    print("✓ Valid PES file")
    
    # Extract header info
    version = struct.unpack('<I', data[8:12])[0]
    hoop_count = struct.unpack('<H', data[12:14])[0]
    width = struct.unpack('<H', data[16:18])[0]
    height = struct.unpack('<H', data[18:20])[0]
    
    print(f"Version: {version}")
    print(f"Hoop count: {hoop_count}")
    print(f"Dimensions: {width * 0.1:.1f} x {height * 0.1:.1f} mm")
    
    # Count stitches using improved method
    stitch_count = 0
    i = 0
    while i < len(data) - 4:
        # Look for patterns that look like coordinates (2-byte values)
        try:
            val1 = struct.unpack('<H', data[i:i+2])[0]
            val2 = struct.unpack('<H', data[i+2:i+4])[0]
            
            # Check if these look like reasonable coordinates (0-1000 range)
            if 0 < val1 < 1000 and 0 < val2 < 1000:
                stitch_count += 1
                i += 4  # Skip the coordinate pair
            else:
                i += 1
        except:
            i += 1
    
    print(f"Stitch count: {stitch_count}")
    
    # Count other elements
    threads = data.count(b'Thread')
    emb_objects = data.count(b'CEmbOne')
    sew_segments = data.count(b'CSewSeg')
    
    print(f"Threads: {threads}")
    print(f"Embroidery objects: {emb_objects}")
    print(f"Sewing segments: {sew_segments}")
    
    # Quality assessment
    if stitch_count == 0:
        quality = "INVALID"
    elif stitch_count < 20:
        quality = "VERY_SIMPLE"
    elif stitch_count < 100:
        quality = "SIMPLE"
    elif stitch_count < 500:
        quality = "MODERATE"
    else:
        quality = "COMPLEX"
    
    print(f"Quality: {quality}")
    
    return {
        'file_size': len(data),
        'width': width * 0.1,
        'height': height * 0.1,
        'stitch_count': stitch_count,
        'threads': threads,
        'objects': emb_objects,
        'segments': sew_segments,
        'quality': quality
    }

def compare_production_results(api_data, api_claimed):
    """Compare production results with API claims."""
    print(f"\n{'='*60}")
    print("PRODUCTION TEST RESULTS - NICOLE PROJECT")
    print(f"{'='*60}")
    
    print(f"\n📊 API RESPONSE ANALYSIS:")
    print(f"  API Claimed Stitches: {api_claimed['stitchCount']}")
    print(f"  API Claimed Quality: {api_claimed['quality']}")
    print(f"  API Claimed Complexity: {api_claimed['complexity']}")
    print(f"  API Claimed Dimensions: {api_claimed['dimensions']['width']} x {api_claimed['dimensions']['height']} mm")
    
    print(f"\n📊 ACTUAL PES FILE ANALYSIS:")
    print(f"  Actual Stitch Count: {api_data['stitch_count']}")
    print(f"  Actual Quality: {api_data['quality']}")
    print(f"  Actual Dimensions: {api_data['width']:.1f} x {api_data['height']:.1f} mm")
    print(f"  File Size: {api_data['file_size']} bytes")
    print(f"  Threads: {api_data['threads']}")
    print(f"  Objects: {api_data['objects']}")
    print(f"  Segments: {api_data['segments']}")
    
    print(f"\n🔍 ACCURACY CHECK:")
    stitch_diff = abs(api_data['stitch_count'] - api_claimed['stitchCount'])
    if stitch_diff <= 5:
        print(f"  ✅ Stitch count is ACCURATE (diff: {stitch_diff})")
    elif stitch_diff <= 20:
        print(f"  ⚠️  Stitch count is close (diff: {stitch_diff})")
    else:
        print(f"  ❌ Stitch count is INACCURATE (diff: {stitch_diff})")
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if api_data['stitch_count'] == 0:
        print("  ❌ FAIL: No stitches generated - conversion completely failed")
    elif api_data['stitch_count'] < 50:
        print("  ⚠️  CONCERN: Very few stitches - likely just basic shapes")
        print("  🔍 This suggests the SVG path parsing is not working properly")
    elif api_data['stitch_count'] < 200:
        print("  ⚠️  CAUTION: Low stitch count - simple design")
    elif api_data['stitch_count'] < 500:
        print("  ✅ GOOD: Moderate stitch count - reasonable quality")
    else:
        print("  🎉 EXCELLENT: High stitch count - professional quality")
    
    # Check if it's just a basic shape
    if api_data['stitch_count'] < 20 and api_data['objects'] == 1:
        print("  ❌ LIKELY ISSUE: This appears to be just a basic shape, not detailed embroidery")
        print("  🔍 The complex Nicole Project SVG should generate hundreds of stitches")
    elif api_data['stitch_count'] > 100:
        print("  ✅ GOOD: Design appears to have meaningful embroidery content")
    
    print(f"\n📈 COMPARISON WITH LOCAL TEST:")
    print(f"  Local Test Result: 3,289 stitches (professional quality)")
    print(f"  Production Result: {api_data['stitch_count']} stitches ({api_data['quality']} quality)")
    difference = 3289 - api_data['stitch_count']
    print(f"  Difference: {difference} stitches")
    
    if difference > 3000:
        print("  ❌ MAJOR DISCREPANCY: Production is missing most stitches!")
        print("  🔍 This suggests the production Lambda is not using the same code as local")
    elif difference > 500:
        print("  ⚠️  SIGNIFICANT DIFFERENCE: Production is missing many stitches")
    elif difference < 100:
        print("  ✅ GOOD: Production results are close to local test")

if __name__ == "__main__":
    # API response data from the curl output
    api_response = {
        "stitchCount": 17,
        "quality": "basic",
        "complexity": "very_simple",
        "dimensions": {"width": 0.0, "height": 0.0}
    }
    
    # Analyze the production PES file
    production_data = analyze_pes_file("Nicole Project - Production Test.pes", "PRODUCTION (Updated Lambda)")
    
    if production_data:
        compare_production_results(production_data, api_response)
    else:
        print("❌ Could not analyze the production PES file")
