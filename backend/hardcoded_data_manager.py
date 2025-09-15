"""
Hardcoded Data Manager for Fill.ai

This module manages the loading and application of hardcoded form data,
including coordinates, schema overrides, and default values.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import re

class HardcodedDataManager:
    def __init__(self, data_directory="./hardcoded_data"):
        """Initialize the hardcoded data manager"""
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(exist_ok=True)
        self.loaded_data = {}
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all hardcoded data files"""
        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Store by filename and hash for multiple lookup methods
                if 'metadata' in data:
                    file_hash = data['metadata'].get('file_hash')
                    filename = data['metadata'].get('filename')
                    
                    if file_hash:
                        self.loaded_data[file_hash] = data
                    if filename:
                        self.loaded_data[filename] = data
                
                # Also store by the JSON filename itself
                self.loaded_data[json_file.stem] = data
                
                print(f"📁 Loaded hardcoded data: {json_file.name}")
                
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
    
    def get_file_hash(self, file_path):
        """Generate MD5 hash for a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"❌ Error generating hash for {file_path}: {e}")
            return None
    
    def find_hardcoded_data(self, image_path):
        """Find hardcoded data for a given image"""
        # Method 1: Try by file hash
        file_hash = self.get_file_hash(image_path)
        if file_hash and file_hash in self.loaded_data:
            print(f"✅ Found hardcoded data by hash: {file_hash}")
            return self.loaded_data[file_hash]
        
        # Method 2: Try by filename
        filename = Path(image_path).name
        if filename in self.loaded_data:
            print(f"✅ Found hardcoded data by filename: {filename}")
            return self.loaded_data[filename]
        
        # Method 3: Try by filename without extension
        filename_no_ext = Path(image_path).stem
        if filename_no_ext in self.loaded_data:
            print(f"✅ Found hardcoded data by filename stem: {filename_no_ext}")
            return self.loaded_data[filename_no_ext]
        
        print(f"❌ No hardcoded data found for: {filename}")
        return None
    
    def apply_hardcoded_schema(self, original_schema, image_path):
        """Apply hardcoded schema modifications if available"""
        hardcoded_data = self.find_hardcoded_data(image_path)
        if not hardcoded_data:
            return original_schema
        
        # Use hardcoded schema if available, otherwise use original
        if 'schema' in hardcoded_data:
            print("🔧 Using hardcoded schema")
            return hardcoded_data['schema']
        
        return original_schema
    
    def apply_hardcoded_coordinates(self, original_coordinates, image_path):
        """Apply hardcoded coordinates if available"""
        hardcoded_data = self.find_hardcoded_data(image_path)
        if not hardcoded_data:
            return original_coordinates
        
        # Use hardcoded coordinates if available
        if 'coordinates' in hardcoded_data and hardcoded_data['coordinates']:
            print(f"🎯 Using hardcoded coordinates ({len(hardcoded_data['coordinates'])} fields)")
            return hardcoded_data['coordinates']
        
        return original_coordinates
    
    def apply_hardcoded_values(self, schema, image_path):
        """Apply hardcoded values to schema fields"""
        hardcoded_data = self.find_hardcoded_data(image_path)
        if not hardcoded_data or 'hardcoded_values' not in hardcoded_data:
            return schema
        
        hardcoded_values = hardcoded_data['hardcoded_values']
        applied_count = 0
        
        # Extract fields from schema
        fields = []
        if "fields" in schema:
            fields = schema["fields"]
        elif "sections" in schema:
            for section in schema["sections"]:
                fields.extend(section.get("fields", []))
        
        # Apply hardcoded values to matching fields
        for field in fields:
            if field.get('value'):  # Skip fields that already have values
                continue
                
            field_name = field.get('name', '')
            field_label = field.get('label', '')
            
            # Try multiple matching strategies
            matched_value = None
            
            # Direct name match
            if field_name in hardcoded_values:
                matched_value = hardcoded_values[field_name]
            
            # Direct label match (normalized)
            elif field_label:
                normalized_label = field_label.lower().replace(' ', '_').replace('-', '_')
                normalized_label = re.sub(r'[^a-zA-Z0-9_]', '', normalized_label)
                if normalized_label in hardcoded_values:
                    matched_value = hardcoded_values[normalized_label]
            
            # Fuzzy matching
            if not matched_value:
                for key, value in hardcoded_values.items():
                    # Check if key is contained in field name/label or vice versa
                    if (key.lower() in field_name.lower() or 
                        key.lower() in field_label.lower() or
                        field_name.lower() in key.lower() or
                        field_label.lower().replace(' ', '_') in key.lower()):
                        matched_value = value
                        break
            
            # Apply the matched value
            if matched_value:
                field['value'] = matched_value
                applied_count += 1
                print(f"🔧 Hardcoded: {field.get('label', field_name)} = {matched_value}")
        
        if applied_count > 0:
            print(f"✅ Applied {applied_count} hardcoded values")
        
        return schema
    
    def get_complete_hardcoded_data(self, image_path):
        """Get all hardcoded data for a form"""
        return self.find_hardcoded_data(image_path)
    
    def list_available_data(self):
        """List all available hardcoded data"""
        print("\n📋 Available Hardcoded Data:")
        for key, data in self.loaded_data.items():
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"  📄 {key}")
                print(f"     Form: {metadata.get('form_title', 'Unknown')}")
                print(f"     File: {metadata.get('filename', 'Unknown')}")
                print(f"     Fields: {len(data.get('hardcoded_values', {}))}")
                print(f"     Coordinates: {len(data.get('coordinates', {}))}")
                print()
    
    def create_hardcoded_entry(self, image_path, schema, coordinates, hardcoded_values, form_title=None):
        """Create a new hardcoded data entry"""
        file_hash = self.get_file_hash(image_path)
        filename = Path(image_path).name
        
        data = {
            'metadata': {
                'filename': filename,
                'file_hash': file_hash,
                'form_title': form_title or 'Custom Form',
                'created_at': datetime.now().isoformat()
            },
            'schema': schema,
            'coordinates': coordinates,
            'hardcoded_values': hardcoded_values
        }
        
        # Save to file
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', form_title or 'custom')
        output_file = self.data_dir / f"{safe_title}_{file_hash[:8]}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Reload data
        self._load_all_data()
        
        print(f"💾 Created hardcoded data entry: {output_file}")
        return output_file

# Global instance for easy importing
hardcoded_manager = HardcodedDataManager()

# Convenience functions for backward compatibility
def get_value_for_field(field_label, field_type='text'):
    """Get hardcoded value for a field (backward compatibility)"""
    # This is a simplified version for compatibility with existing code
    common_values = {
        'family_name': 'Smith',
        'given_name': 'John',
        'middle_name': 'Michael',
        'email': 'john.smith@example.com',
        'phone': '+1-555-123-4567',
        'date_of_birth': '01/15/1990'
    }
    
    field_key = field_label.lower().replace(' ', '_').replace('-', '_')
    field_key = re.sub(r'[^a-zA-Z0-9_]', '', field_key)
    
    for key, value in common_values.items():
        if key in field_key or field_key in key:
            return value
    
    return None

if __name__ == "__main__":
    # Test the manager
    manager = HardcodedDataManager()
    manager.list_available_data()