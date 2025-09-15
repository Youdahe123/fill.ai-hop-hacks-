#!/usr/bin/env python3
"""
Fill.ai Hardcoding Workflow CLI

A simple command-line interface for extracting and managing hardcoded form data.

Usage:
    python hardcode_cli.py extract form_image.jpg
    python hardcode_cli.py interactive form_image.jpg
    python hardcode_cli.py list
    python hardcode_cli.py test form_image.jpg
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append('.')
sys.path.append('./server')

def main():
    if len(sys.argv) < 2:
        print_help()
        return 1
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'extract':
            if len(sys.argv) < 3:
                print("❌ Please provide an image path")
                print("Usage: python hardcode_cli.py extract form_image.jpg")
                return 1
            
            image_path = sys.argv[2]
            return extract_data(image_path)
        
        elif command == 'interactive':
            if len(sys.argv) < 3:
                print("❌ Please provide an image path")
                print("Usage: python hardcode_cli.py interactive form_image.jpg")
                return 1
            
            image_path = sys.argv[2]
            return interactive_mode(image_path)
        
        elif command == 'list':
            return list_hardcoded_data()
        
        elif command == 'test':
            if len(sys.argv) < 3:
                print("❌ Please provide an image path")
                print("Usage: python hardcode_cli.py test form_image.jpg")
                return 1
            
            image_path = sys.argv[2]
            return test_hardcoded_data(image_path)
        
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
            return 1
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def print_help():
    """Print help information"""
    print("""
🤖 Fill.ai Hardcoding Workflow CLI

Commands:
  extract <image>     Extract schema and coordinates from a form image
  interactive <image> Interactive mode - extract, edit, and save hardcoded data
  list               List all available hardcoded data files
  test <image>       Test if hardcoded data exists for an image

Examples:
  python hardcode_cli.py extract sample_data/form.jpg
  python hardcode_cli.py interactive sample_data/form.jpg
  python hardcode_cli.py list
  python hardcode_cli.py test sample_data/form.jpg

Workflow:
  1. Use 'extract' or 'interactive' to create hardcoded data from a form
  2. Edit the generated JSON file to customize values and coordinates
  3. Use 'test' to verify the hardcoded data is loaded correctly
  4. The system will automatically use hardcoded data when processing forms
""")

def extract_data(image_path):
    """Extract data from a form image"""
    try:
        from coordinate_extractor_tool import FormDataExtractor
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return 1
        
        print(f"🔍 Extracting data from: {image_path}")
        extractor = FormDataExtractor()
        data = extractor.extract_complete_data(image_path)
        
        if data:
            output_file = extractor.save_data(data)
            print(f"✅ Extraction complete!")
            print(f"📄 Data saved to: {output_file}")
            print(f"📊 Found {len(data.get('coordinates', {}))} coordinates")
            print(f"🏷️  Found {len(data.get('hardcoded_values', {}))} field templates")
            
            print(f"\n💡 Next steps:")
            print(f"1. Edit the hardcoded_values section in: {output_file}")
            print(f"2. Adjust coordinates if needed")
            print(f"3. Test with: python hardcode_cli.py test {image_path}")
            
            return 0
        else:
            print("❌ Failed to extract data")
            return 1
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed and paths are correct")
        return 1

def interactive_mode(image_path):
    """Run interactive extraction mode"""
    try:
        from coordinate_extractor_tool import FormDataExtractor
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return 1
        
        print(f"🚀 Starting interactive mode for: {image_path}")
        extractor = FormDataExtractor()
        extractor.interactive_mode(image_path)
        return 0
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1

def list_hardcoded_data():
    """List all available hardcoded data"""
    try:
        from hardcoded_data_manager import hardcoded_manager
        
        print("📋 Available Hardcoded Data:")
        hardcoded_manager.list_available_data()
        return 0
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1

def test_hardcoded_data(image_path):
    """Test if hardcoded data exists for an image"""
    try:
        from hardcoded_data_manager import hardcoded_manager
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return 1
        
        print(f"🧪 Testing hardcoded data for: {image_path}")
        
        # Test hash lookup
        file_hash = hardcoded_manager.get_file_hash(image_path)
        print(f"📋 File hash: {file_hash}")
        
        # Test data lookup
        data = hardcoded_manager.find_hardcoded_data(image_path)
        
        if data:
            print("✅ Hardcoded data found!")
            metadata = data.get('metadata', {})
            print(f"🏷️  Form title: {metadata.get('form_title', 'Unknown')}")
            print(f"📄 Original file: {metadata.get('filename', 'Unknown')}")
            print(f"📊 Coordinates: {len(data.get('coordinates', {}))}")
            print(f"🔧 Hardcoded values: {len(data.get('hardcoded_values', {}))}")
            
            # Show some example values
            hardcoded_values = data.get('hardcoded_values', {})
            if hardcoded_values:
                print(f"\n💡 Sample hardcoded values:")
                for key, value in list(hardcoded_values.items())[:5]:
                    print(f"   {key}: {value}")
                if len(hardcoded_values) > 5:
                    print(f"   ... and {len(hardcoded_values) - 5} more")
            
            return 0
        else:
            print("❌ No hardcoded data found for this image")
            print(f"\n💡 To create hardcoded data:")
            print(f"   python hardcode_cli.py interactive {image_path}")
            return 1
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())