"""
Hardcoded Values Manager for Fill.ai
"""
import json
import os

class HardcodedValuesManager:
    def __init__(self, values_file="hardcoded_values.json"):
        self.values_file = values_file
        self.values = self.load_hardcoded_values()
    
    def load_hardcoded_values(self):
        """Load hardcoded values from JSON file"""
        try:
            if os.path.exists(self.values_file):
                with open(self.values_file, 'r') as f:
                    values = json.load(f)
                print(f"✅ Loaded hardcoded values from {self.values_file}")
                return values
            else:
                print(f"⚠️ Hardcoded values file {self.values_file} not found")
                return {}
        except Exception as e:
            print(f"❌ Error loading hardcoded values: {e}")
            return {}
    
    def get_value_for_field(self, field_label, field_type="text"):
        """Get hardcoded value for a specific field"""
        field_key = field_label.lower().replace(' ', '_').replace('-', '_')
        
        # Check all categories for matching field
        for category, fields in self.values.items():
            if isinstance(fields, dict):
                for key, value in fields.items():
                    if (key in field_key or field_key in key or 
                        any(word in field_key for word in key.split('_'))):
                        print(f"🔧 Found hardcoded value for '{field_label}': {value}")
                        return value
        
        # Direct key match
        if field_key in self.values:
            print(f"🔧 Found direct hardcoded value for '{field_label}': {self.values[field_key]}")
            return self.values[field_key]
        
        return None
    
    def apply_to_schema(self, schema):
        """Apply hardcoded values to schema fields"""
        if 'fields' in schema:
            for field in schema['fields']:
                if not field.get('value'):  # Only fill empty fields
                    hardcoded_value = self.get_value_for_field(
                        field.get('label', ''), 
                        field.get('type', 'text')
                    )
                    if hardcoded_value:
                        field['value'] = hardcoded_value
        return schema
    
    def get_all_values_flat(self):
        """Get all hardcoded values as a flat dictionary"""
        flat_values = {}
        for category, fields in self.values.items():
            if isinstance(fields, dict):
                flat_values.update(fields)
            else:
                flat_values[category] = fields
        return flat_values

# Global instance
hardcoded_manager = HardcodedValuesManager()