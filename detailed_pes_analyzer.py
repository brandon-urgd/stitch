#!/usr/bin/env python3
"""
Detailed PES File Analyzer - More accurate stitch counting and analysis
"""

import struct
import sys

def analyze_pes_detailed(filename):
    """Detailed analysis of PES file with better stitch detection"""
    print(f"Detailed PES Analysis: {filename}")
    print("=" * 60)
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    
    # Verify PES format
    if data[:8] != b'#PES0060':
        print("✗ Not a valid PES file")
        return
    
    print("✓ Valid PES file format")
    
    # Parse header information
    try:
        # Read header fields
        version = struct.unpack('<I', data[8:12])[0]
        hoop_count = struct.unpack('<H', data[12:14])[0]
        width = struct.unpack('<H', data[16:18])[0]
        height = struct.unpack('<H', data[18:20])[0]
        
        print(f"Version: {version}")
        print(f"Hoop count: {hoop_count}")
        print(f"Design size: {width} x {height}")
        
        # Look for stitch data more carefully
        stitch_commands = []
        stitch_count = 0
        
        # Search for stitch command patterns
        i = 0
        while i < len(data) - 2:
            # Look for stitch command bytes
            byte1 = data[i]
            byte2 = data[i + 1] if i + 1 < len(data) else 0
            
            # Stitch commands typically have specific patterns
            if byte1 == 0x00 and byte2 in [0x01, 0x02, 0x03, 0x04, 0x05]:
                stitch_commands.append((i, byte1, byte2))
                stitch_count += 1
                i += 2
            elif byte1 == 0x80 and byte2 == 0x00:  # Jump stitch
                stitch_commands.append((i, byte1, byte2))
                stitch_count += 1
                i += 2
            else:
                i += 1
        
        print(f"Stitch commands found: {stitch_count}")
        
        # Look for coordinate data (stitch positions)
        coordinate_pairs = 0
        for i in range(len(data) - 4):
            # Look for patterns that might be coordinates
            if i + 4 < len(data):
                # Check for small integer values that could be coordinates
                val1 = struct.unpack('<H', data[i:i+2])[0]
                val2 = struct.unpack('<H', data[i+2:i+4])[0]
                
                # Coordinates are typically small positive values
                if 0 < val1 < 1000 and 0 < val2 < 1000:
                    coordinate_pairs += 1
        
        print(f"Potential coordinate pairs: {coordinate_pairs}")
        
        # Count specific PES elements
        thread_count = data.count(b'Thread')
        emb_objects = data.count(b'CEmbOne')
        sew_segments = data.count(b'CSewSeg')
        
        print(f"Thread definitions: {thread_count}")
        print(f"Embroidery objects: {emb_objects}")
        print(f"Sewing segments: {sew_segments}")
        
        # Analyze the actual stitch data
        print("\nStitch Data Analysis:")
        print("-" * 30)
        
        if stitch_count > 0:
            print(f"✓ Found {stitch_count} stitch commands")
            
            # Show first few stitch commands
            print("First few stitch commands:")
            for i, (pos, b1, b2) in enumerate(stitch_commands[:10]):
                print(f"  Position {pos}: 0x{b1:02x} 0x{b2:02x}")
            
            if len(stitch_commands) > 10:
                print(f"  ... and {len(stitch_commands) - 10} more")
        else:
            print("⚠ No stitch commands detected")
        
        # Quality assessment
        print("\nQuality Assessment:")
        print("-" * 20)
        
        if stitch_count == 0:
            print("❌ CRITICAL: No stitch data found - this is not a valid embroidery file")
        elif stitch_count < 10:
            print("⚠ WARNING: Very few stitches - likely just a basic shape or square")
        elif stitch_count < 50:
            print("⚠ CAUTION: Low stitch count - simple design")
        elif stitch_count < 200:
            print("✓ GOOD: Moderate stitch count - reasonable complexity")
        else:
            print("✓ EXCELLENT: High stitch count - complex, detailed design")
        
        # Check for meaningful content vs just a square
        if stitch_count > 0 and coordinate_pairs > 0:
            if stitch_count < 20 and coordinate_pairs < 10:
                print("❌ LIKELY ISSUE: This appears to be just a basic square or simple shape")
            else:
                print("✓ Design appears to have meaningful embroidery content")
        
        # Final verdict
        print("\nFinal Verdict:")
        print("-" * 15)
        if stitch_count == 0:
            print("❌ FAIL: This PES file contains no stitch data")
        elif stitch_count < 20:
            print("⚠ CONCERN: This appears to be just a basic shape, not a proper embroidery design")
        else:
            print("✓ PASS: This appears to be a valid embroidery design with reasonable complexity")
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python detailed_pes_analyzer.py <pes_file>")
        sys.exit(1)
    
    analyze_pes_detailed(sys.argv[1])
