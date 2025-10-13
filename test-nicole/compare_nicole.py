#!/usr/bin/env python3
"""
Compare Nicole Project conversion before and after Lambda updates
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
    while i < len(data) - 1:
        byte1 = data[i]
        byte2 = data[i + 1] if i + 1 < len(data) else 0
        
        if byte1 == 0x00 and byte2 in [0x01, 0x02, 0x03, 0x04, 0x05]:
            stitch_count += 1
            i += 2
        elif byte1 == 0x80 and byte2 == 0x00:
            stitch_count += 1
            i += 2
        elif byte1 == 0x00 and byte2 == 0x00:
            break
        else:
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

def compare_results(old_data, new_data, api_response):
    """Compare the before and after results."""
    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print(f"{'='*60}")
    
    print(f"\n📊 STITCH COUNT:")
    print(f"  Before: {old_data['stitch_count']} stitches")
    print(f"  After:  {new_data['stitch_count']} stitches")
    print(f"  API Claimed: {api_response['stitchCount']} stitches")
    
    improvement = new_data['stitch_count'] - old_data['stitch_count']
    if old_data['stitch_count'] > 0:
        print(f"  Improvement: +{improvement} stitches ({improvement/old_data['stitch_count']*100:.1f}% increase)")
    else:
        print(f"  Improvement: +{improvement} stitches (from 0 to {new_data['stitch_count']})")
    
    print(f"\n📏 DIMENSIONS:")
    print(f"  Before: {old_data['width']:.1f} x {old_data['height']:.1f} mm")
    print(f"  After:  {new_data['width']:.1f} x {new_data['height']:.1f} mm")
    
    if old_data['width'] == 0 and new_data['width'] > 0:
        print("  ✅ FIXED: Dimensions now properly set")
    elif new_data['width'] > old_data['width']:
        print("  ✅ IMPROVED: Dimensions increased")
    else:
        print("  ⚠️  Dimensions unchanged")
    
    print(f"\n🎯 QUALITY ASSESSMENT:")
    print(f"  Before: {old_data['quality']}")
    print(f"  After:  {new_data['quality']}")
    print(f"  API Quality: {api_response['quality']}")
    
    print(f"\n📁 FILE STRUCTURE:")
    print(f"  Before: {old_data['objects']} objects, {old_data['segments']} segments")
    print(f"  After:  {new_data['objects']} objects, {new_data['segments']} segments")
    
    print(f"\n🔍 ACCURACY VERIFICATION:")
    api_stitches = api_response['stitchCount']
    actual_stitches = new_data['stitch_count']
    
    if abs(api_stitches - actual_stitches) <= 5:
        print("  ✅ API stitch count is ACCURATE")
    elif abs(api_stitches - actual_stitches) <= 20:
        print("  ⚠️  API stitch count is close but not exact")
    else:
        print("  ❌ API stitch count is INACCURATE")
    
    print(f"\n📈 OVERALL IMPROVEMENT:")
    if new_data['stitch_count'] > 0 and old_data['stitch_count'] == 0:
        print("  🎉 MASSIVE IMPROVEMENT: Went from 0 to actual stitches!")
    elif new_data['stitch_count'] > old_data['stitch_count'] * 2:
        print("  🚀 SIGNIFICANT IMPROVEMENT: Stitch count more than doubled!")
    elif new_data['stitch_count'] > old_data['stitch_count']:
        print("  ✅ IMPROVEMENT: Stitch count increased")
    else:
        print("  ⚠️  No improvement in stitch count")

if __name__ == "__main__":
    # Analyze both files
    old_data = analyze_pes_file("/Users/brandon/Desktop/Output PES", "BEFORE (Old Lambda)")
    new_data = analyze_pes_file("Nicole Project - New.pes", "AFTER (New Lambda)")
    
    # API response data
    api_response = {
        'stitchCount': 375,
        'quality': 'professional',
        'complexity': 'moderate',
        'dimensions': {'width': 100.0, 'height': 100.0}
    }
    
    # Compare results
    if old_data and new_data:
        compare_results(old_data, new_data, api_response)
    else:
        print("❌ Could not analyze one or both files")
