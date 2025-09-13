#!/usr/bin/env python3
"""
Simple script to adjust last name coordinates to be lower
"""
import json
import os
import sys

def adjust_last_name_coordinates(coordinates_file):
    """
    Adjust last name field to be positioned lower
    """
    if not os.path.exists(coordinates_file):
        print(f"❌ Coordinate file not found: {coordinates_file}")
        return False
    
    # Load coordinates
    with open(coordinates_file, 'r') as f:
        coordinates = json.load(f)
    
    print(f"📋 Original coordinates: {len(coordinates)} fields")
    
    # Find and adjust last name field
    last_name_variations = ['last_name', 'lastname', 'last name', 'surname', 'family_name']
    adjusted = False
    
    for field_name, coords in coordinates.items():
        field_lower = field_name.lower()
        if any(variation in field_lower for variation in last_name_variations):
            x, y = coords
            new_y = y + 0.05  # Move down by 5% of page height
            coordinates[field_name] = [x, new_y]
            print(f"📝 Adjusted {field_name}: ({x:.3f}, {y:.3f}) → ({x:.3f}, {new_y:.3f})")
            adjusted = True
            break
    
    if not adjusted:
        print("⚠️ No last name field found to adjust")
        return False
    
    # Save adjusted coordinates
    with open(coordinates_file, 'w') as f:
        json.dump(coordinates, f, indent=2)
    
    print(f"✅ Updated coordinates saved to: {coordinates_file}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        coordinates_file = sys.argv[1]
    else:
        # Look for coordinate files in current directory
        coordinate_files = [f for f in os.listdir('.') if f.endswith('_coordinates.json')]
        if coordinate_files:
            coordinates_file = coordinate_files[0]
            print(f"🔍 Found coordinate file: {coordinates_file}")
        else:
            print("❌ No coordinate files found. Please specify a file path.")
            sys.exit(1)
    
    adjust_last_name_coordinates(coordinates_file)
