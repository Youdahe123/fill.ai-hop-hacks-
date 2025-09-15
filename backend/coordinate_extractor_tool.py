#!/usr/bin/env python3
"""
Coordinate Extraction Tool for Fill.ai

This tool extracts schema and coordinate data from forms, allowing you to:
1. Analyze a form and get complete schema + coordinate data
2. Save the data in an editable format
3. Use the data as hardcoded values in your application

Usage:
    python coordinate_extractor_tool.py --extract path/to/form.jpg
    python coordinate_extractor_tool.py --interactive path/to/form.jpg
"""

import os
import json
import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path
import sys

# Add server directory to path
sys.path.append('./server')
from practice import extract_and_generate_schema
from enhanced_coordinate_extractor import CoordinateExtractor
from dotenv import load_dotenv

load_dotenv()

class FormDataExtractor:
    def __init__(self):
        """Initialize the form data extractor"""
        # Initialize Azure coordinate extractor
        endpoint = os.getenv('AZURE_ENDPOINT', 'https://aiformfilling-doc-ai.cognitiveservices.azure.com/')
        key = os.getenv('AZURE_KEY')
        if not key:
            raise ValueError("AZURE_KEY not found in environment variables")
        
        self.coordinate_extractor = CoordinateExtractor(endpoint, key)
        self.output_dir = Path('./hardcoded_data')
        self.output_dir.mkdir(exist_ok=True)
        
    def get_file_hash(self, file_path):
        """Generate a unique hash for the file for identification"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    def extract_complete_data(self, image_path):
        """Extract both schema and coordinate data from a form"""
        print(f"🔍 Analyzing form: {image_path}")
        
        # Step 1: Extract schema using existing function
        print("📋 Extracting schema...")
        schema_result = extract_and_generate_schema(image_path)
        
        if not schema_result or not schema_result.get('success'):
            print("❌ Failed to extract schema")
            return None
        
        # Step 2: Extract coordinates using Azure
        print("📐 Extracting coordinates...")
        coordinates = self.coordinate_extractor.get_coordinate_mapping(image_path)
        
        # Step 3: Generate file hash for identification
        file_hash = self.get_file_hash(image_path)
        filename = Path(image_path).name
        
        # Step 4: Combine all data
        complete_data = {
            'metadata': {
                'filename': filename,
                'file_hash': file_hash,
                'extracted_at': datetime.now().isoformat(),
                'form_title': schema_result.get('form_title', 'Unknown Form')
            },
            'schema': schema_result['schema'],
            'coordinates': coordinates or {},
            'hardcoded_values': self._generate_hardcoded_template(schema_result['schema']),
            'field_mapping': self._create_field_mapping(schema_result['schema'], coordinates or {})
        }
        
        return complete_data
    
    def _generate_hardcoded_template(self, schema):
        """Generate a template for hardcoded values based on schema fields"""
        hardcoded_template = {}
        
        # Extract fields from schema
        fields = []
        if "fields" in schema:
            fields = schema["fields"]
        elif "sections" in schema:
            for section in schema["sections"]:
                fields.extend(section.get("fields", []))
        
        # Create template entries for each field
        for field in fields:
            field_name = field.get('name', '')
            field_label = field.get('label', '')
            field_type = field.get('type', 'text')
            
            # Create a clean field key
            key = field_name or field_label.lower().replace(' ', '_').replace('-', '_')
            key = re.sub(r'[^a-zA-Z0-9_]', '', key)
            
            if key:
                # Add sample values based on field type
                if field_type == 'email':
                    hardcoded_template[key] = "example@email.com"
                elif field_type == 'phone':
                    hardcoded_template[key] = "+1-555-123-4567"
                elif field_type == 'date':
                    hardcoded_template[key] = "01/01/2000"
                elif 'name' in key.lower():
                    if 'first' in key.lower() or 'given' in key.lower():
                        hardcoded_template[key] = "John"
                    elif 'last' in key.lower() or 'family' in key.lower():
                        hardcoded_template[key] = "Smith"
                    elif 'middle' in key.lower():
                        hardcoded_template[key] = "Michael"
                    else:
                        hardcoded_template[key] = "Sample Name"
                else:
                    hardcoded_template[key] = f"Sample {field_label or field_name}"
        
        return hardcoded_template
    
    def _create_field_mapping(self, schema, coordinates):
        """Create a mapping between schema fields and coordinates"""
        mapping = {}
        
        # Extract fields from schema
        fields = []
        if "fields" in schema:
            fields = schema["fields"]
        elif "sections" in schema:
            for section in schema["sections"]:
                fields.extend(section.get("fields", []))
        
        # Match fields with coordinates
        for field in fields:
            field_name = field.get('name', '')
            field_label = field.get('label', '')
            
            # Try to find matching coordinate
            coord_key = None
            for coord_name in coordinates.keys():
                if (field_name and coord_name.lower() == field_name.lower()) or \
                   (field_label and coord_name.lower() == field_label.lower().replace(' ', '_')):
                    coord_key = coord_name
                    break
            
            if coord_key:
                mapping[field_name or field_label] = {
                    'coordinate_key': coord_key,
                    'position': coordinates[coord_key],
                    'field_type': field.get('type', 'text'),
                    'required': field.get('required', False)
                }
        
        return mapping
    
    def save_data(self, data, custom_filename=None):
        """Save extracted data to a JSON file"""
        if custom_filename:
            filename = custom_filename
        else:
            # Generate filename based on form title and hash
            safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', data['metadata']['form_title'])
            filename = f"{safe_title}_{data['metadata']['file_hash'][:8]}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to: {output_path}")
        return output_path
    
    def interactive_mode(self, image_path):
        """Interactive mode for extracting and editing data"""
        print("🚀 Starting interactive extraction mode...")
        
        # Extract data
        data = self.extract_complete_data(image_path)
        if not data:
            return
        
        # Display summary
        print(f"\n📊 Extraction Summary:")
        print(f"Form Title: {data['metadata']['form_title']}")
        print(f"Schema Fields: {len(data.get('schema', {}).get('fields', []))}")
        print(f"Coordinates Found: {len(data.get('coordinates', {}))}")
        print(f"Hardcoded Template: {len(data.get('hardcoded_values', {}))}")
        
        # Save initial data
        temp_file = self.save_data(data, f"temp_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        print(f"\n📝 Edit the hardcoded_values section in: {temp_file}")
        print("💡 You can modify:")
        print("  - hardcoded_values: Set your desired default values")
        print("  - coordinates: Adjust field positions if needed")
        print("  - field_mapping: Update field relationships")
        
        input("\n⏸️  Press Enter when you're done editing the file...")
        
        # Reload the edited data
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                edited_data = json.load(f)
            
            # Save as final version
            final_file = self.save_data(edited_data, f"hardcoded_{data['metadata']['form_title'].replace(' ', '_')}.json")
            print(f"✅ Final hardcoded data saved to: {final_file}")
            
            # Show how to use it
            print(f"\n🔧 To use this data in your application:")
            print(f"1. Place the file in your hardcoded_data directory")
            print(f"2. The system will automatically detect and use it for forms with hash: {data['metadata']['file_hash']}")
            print(f"3. Or reference it by filename: {data['metadata']['filename']}")
            
        except Exception as e:
            print(f"❌ Error reading edited file: {e}")

def main():
    parser = argparse.ArgumentParser(description='Extract and hardcode form data')
    parser.add_argument('--extract', type=str, help='Extract data from form image')
    parser.add_argument('--interactive', type=str, help='Interactive extraction mode')
    parser.add_argument('--output', type=str, help='Custom output filename')
    
    args = parser.parse_args()
    
    try:
        extractor = FormDataExtractor()
        
        if args.extract:
            print("🔍 Extracting form data...")
            data = extractor.extract_complete_data(args.extract)
            if data:
                output_file = extractor.save_data(data, args.output)
                print(f"✅ Extraction complete! Data saved to: {output_file}")
        
        elif args.interactive:
            extractor.interactive_mode(args.interactive)
        
        else:
            print("Please specify --extract or --interactive with a form image path")
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())