from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
import json
import os
import re
from dotenv import load_dotenv
import time
import sys

# Import hardcoded data manager
sys.path.append('..')
try:
    from hardcoded_data_manager import hardcoded_manager
    HARDCODED_MANAGER_AVAILABLE = True
    print("✅ Hardcoded data manager loaded")
except ImportError:
    HARDCODED_MANAGER_AVAILABLE = False
    print("⚠️ Hardcoded data manager not available")

load_dotenv()
Client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Azure setup
endpoint = 'https://aiformfilling-doc-ai.cognitiveservices.azure.com/'
key = os.getenv('AZURE_KEY')
client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
res = []

def apply_hardcoded_values(schema):
    """
    Apply hardcoded values to specific fields in the schema.
    This function provides fallback values when the hardcoded data manager is not available.
    """
    # Use the hardcoded data manager if available
    if HARDCODED_MANAGER_AVAILABLE:
        # This is now handled in extract_and_generate_schema
        return schema
    
    # Fallback: Define basic hardcoded values here
    hardcoded_values = {
        'family_name': 'Smith',
        'given_name': 'John',
        'middle_name': 'Michael',
        'email': 'john.smith@example.com',
        'phone': '+1-555-123-4567',
        'date_of_birth': '01/15/1990',
        'address': '123 Main Street, City, State 12345',
        'country': 'United States',
        'occupation': 'Software Engineer'
    }
    
    # Apply hardcoded values to matching fields
    if 'fields' in schema:
        for field in schema['fields']:
            field_label = field.get('label', '').lower().replace(' ', '_').replace('-', '_')
            field_name = field.get('name', '').lower().replace(' ', '_').replace('-', '_')
            
            # Check if we have a hardcoded value for this field
            for key, value in hardcoded_values.items():
                if (key in field_label or key in field_name or 
                    field_label in key or field_name in key):
                    field['value'] = value
                    print(f"🔧 Hardcoded value set: {field.get('label', 'Unknown')} = {value}")
                    break
    
    return schema

def extract_and_generate_schema(image_path):
    """
    Main function to extract form structure and generate a schema using Azure OCR and OpenAI
    Now enhanced with hardcoded data support
    """
    
    # Check for hardcoded data first
    if HARDCODED_MANAGER_AVAILABLE:
        hardcoded_data = hardcoded_manager.find_hardcoded_data(image_path)
        if hardcoded_data:
            print("🎯 Using hardcoded schema and data")
            schema = hardcoded_data.get('schema', {})
            # Apply hardcoded values
            schema = hardcoded_manager.apply_hardcoded_values(schema, image_path)
            
            return {
                'success': True,
                'schema': schema,
                'fields': schema.get('fields', []),
                'form_title': hardcoded_data.get('metadata', {}).get('form_title', 'Unknown Form'),
                'raw_text': ['Using hardcoded data'],
                'azure_time': 0,
                'openai_time': 0,
                'hardcoded': True
            }
    
    # Continue with normal extraction if no hardcoded data found
    try:
        azure_start = time.time()
        
        # Determine content type based on file extension
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext == '.pdf':
            content_type = "application/pdf"
        elif file_ext in ['.jpg', '.jpeg']:
            content_type = "image/jpeg"
        elif file_ext == '.png':
            content_type = "image/png"
        else:
            content_type = "image/jpeg"  # default
        
        # Analyze document with Azure Document Intelligence
        with open(image_path, "rb") as f:
            poller = client.begin_analyze_document(
                model_id="prebuilt-layout",
                body=f,
                content_type=content_type
            )
        result = poller.result()
        azure_time = time.time() - azure_start
        print(f"✅ Azure OCR completed in {azure_time:.2f}s")
        
        # Collect all lines from the document
        lines = []
        for page in result.pages:
            for line in page.lines:
                lines.append(line.content)
        
        print(f"📝 Extracted {len(lines)} text lines from document")
        
        # Generate schema using OpenAI
        openai_start = time.time()
        messages = [
            {
                'role': 'system',
                'content': (
                    "You are an assistant that takes lines from a scanned form and reconstructs a JSON form schema. "
                    "Return ONLY valid JSON in your response. For each section of the form, have a value section that will be filled in later. "
                    "Make sure to adjust for questions that require select-if questions and for questions that have conditions. "
                    "Each field should have these sections: type, required, options, accessibility, and value. "
                    "IMPORTANT: Also extract the title/name of the form from the document and include it in the response as 'form_title'."
                )
            },
            {
                'role': 'user',
                'content': (
                    "Here are the lines from the form:\n" +
                    "\n".join(lines) +
                    "\nReturn ONLY valid JSON. Instead of deeply nested objects, represent each field as a flat entry in a 'fields' array. "
                    "Each field object should include: label, section (if applicable), type, required, options (if any), accessibility, and value (empty for now). "
                    "Organize sections using a 'section' field, but keep each field as its own object. "
                    "MUST include a 'form_title' field at the root level with the title/name of the form extracted from the text."
                )
            }
        ]

        response = Client.chat.completions.create(
            model='gpt-4-1106-preview',
            messages=messages,
            max_tokens=2048,
            temperature=0
        )
        answer = response.choices[0].message.content
        openai_time = time.time() - openai_start
        print(f"✅ OpenAI schema generation completed in {openai_time:.2f}s")
        
        # Clean up the response
        if answer.strip().startswith("```"):
            answer = re.sub(r"^```[a-zA-Z]*\n?", "", answer.strip())
            answer = re.sub(r"\n?```$", "", answer.strip())

        try:
            structured = json.loads(answer)
            form_title = structured.get('form_title', 'Unknown Form')
            
            # Apply hardcoded values
            structured = apply_hardcoded_values(structured)
            
            print(f"✅ Successfully generated schema for '{form_title}' with {len(structured.get('fields', []))} fields")
            
            return {
                'success': True,
                'schema': structured,
                'fields': structured.get('fields', []),
                'form_title': form_title,
                'raw_text': lines,
                'azure_time': azure_time,
                'openai_time': openai_time
            }
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse OpenAI response as JSON: {e}")
            return {
                'success': False,
                'error': f'Failed to parse OpenAI response as JSON: {str(e)}',
                'raw_text': lines,
                'azure_time': azure_time,
                'openai_time': openai_time
            }
            
    except Exception as e:
        print(f"❌ Error in extract_and_generate_schema: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'raw_text': [],
            'azure_time': 0,
            'openai_time': 0
        }

# Test function
if __name__ == "__main__":
    # Test with a sample image
    test_path = "sample_data/simple-job-application-form-27d287c8e2b97cd3f175c12ef67426b2-classic.png"
    if os.path.exists(test_path):
        result = extract_and_generate_schema(test_path)
        print("Test result:", json.dumps(result, indent=2))
    else:
        print("Test image not found")
