# Hardcoded Data System for Fill.ai

## Overview

This system allows you to extract schema and coordinate data from forms, then hardcode that data for consistent, fast form filling. Perfect for frequently used forms or when you want to pre-fill specific values.

## Quick Start

### 1. Extract Data from a Form

```bash
# Basic extraction
python hardcode_cli.py extract sample_data/form.jpg

# Interactive mode (recommended)
python hardcode_cli.py interactive sample_data/form.jpg
```

### 2. Edit the Generated Data

The system creates a JSON file like this:

```json
{
  "metadata": {
    "filename": "form.jpg",
    "file_hash": "abc123...",
    "form_title": "Job Application Form"
  },
  "schema": {
    "fields": [...]
  },
  "coordinates": {
    "first_name": [0.2, 0.3],
    "last_name": [0.2, 0.4]
  },
  "hardcoded_values": {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com"
  }
}
```

**Edit the `hardcoded_values` section** to set your desired default values.

### 3. Test Your Hardcoded Data

```bash
python hardcode_cli.py test sample_data/form.jpg
```

### 4. Use in Your Application

The system automatically detects and uses hardcoded data when processing forms:

```python
# In your workflow, the system will automatically:
# 1. Check for hardcoded data by file hash
# 2. Apply hardcoded values to matching fields
# 3. Use hardcoded coordinates for precise positioning
```

## File Organization

```
backend/
├── hardcode_cli.py                 # CLI tool
├── coordinate_extractor_tool.py    # Data extraction
├── hardcoded_data_manager.py       # Data management
├── hardcoded_data/                 # Storage directory
│   ├── Job_Application_abc123.json
│   ├── Tax_Form_def456.json
│   └── ...
```

## CLI Commands

### `extract <image>`
Extracts schema and coordinates, saves to JSON file.

### `interactive <image>`
Interactive mode - extract, pause for editing, then finalize.

### `list`
Shows all available hardcoded data files.

### `test <image>`
Tests if hardcoded data exists for a specific image.

## How It Works

### Form Identification
The system identifies forms using:
1. **File hash** (MD5) - Most reliable
2. **Filename** - Convenient for development
3. **Filename stem** - Fallback option

### Data Application
1. **Schema Override**: Use pre-defined field structure
2. **Coordinate Override**: Use exact field positions
3. **Value Application**: Pre-fill form fields with your data

### Integration Points
- `practice.py`: Schema extraction checks for hardcoded data first
- `websocket_workflow.py`: Applies hardcoded values before conversation
- `image_generator.py`: Uses hardcoded coordinates for positioning

## Example Workflow

```bash
# 1. Analyze a new form
python hardcode_cli.py interactive sample_data/job_application.jpg

# 2. Edit the generated JSON file:
#    - Set hardcoded_values to your preferred defaults
#    - Adjust coordinates if positioning needs tweaking
#    - Modify schema if field detection was incorrect

# 3. Test the setup
python hardcode_cli.py test sample_data/job_application.jpg

# 4. Run your normal workflow - it will use the hardcoded data automatically
python app.py  # or your normal workflow
```

## Benefits

✅ **Faster Processing**: Skip OCR and AI analysis for known forms
✅ **Consistent Results**: Same field detection and positioning every time  
✅ **Custom Defaults**: Pre-fill with your preferred values
✅ **Easy Maintenance**: JSON files are easy to edit and version control
✅ **Flexible Matching**: Works with file hash, filename, or manual assignment

## Tips

- Use `interactive` mode for new forms - it guides you through the process
- File hash matching is most reliable but filename matching is convenient for development
- You can have multiple hardcoded data files for different versions of the same form
- Test your hardcoded data after making changes
- Keep backups of your hardcoded data files - they represent valuable configuration