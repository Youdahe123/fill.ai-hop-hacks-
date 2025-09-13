#!/usr/bin/env python3
"""
Test script to generate a filled form with mock data
"""
import os
import sys
import json
from server.image_generator import FormImageGenerator

def create_mock_coordinates():
    """Create mock coordinates for testing"""
    return {
        "first_name": (0.15, 0.25),
        "last_name": (0.15, 0.30),  # This will be adjusted lower
        "email": (0.15, 0.35),
        "phone": (0.15, 0.40),
        "address": (0.15, 0.45),
        "city": (0.15, 0.50),
        "state": (0.15, 0.55),
        "zip_code": (0.15, 0.60),
        "company_name": (0.15, 0.65),
        "job_title": (0.15, 0.70),
        "start_date": (0.15, 0.75),
        "reason_for_leaving": (0.15, 0.80)
    }

def create_mock_schema():
    """Create mock filled schema for testing"""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
        "phone": "(555) 123-4567",
        "address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "company_name": "Tech Solutions Inc",
        "job_title": "Software Engineer",
        "start_date": "2024-01-15",
        "reason_for_leaving": "Career advancement opportunity"
    }

def test_image_generation():
    """Test the image generation with mock data"""
    print("🧪 Testing Image Generation with Mock Data")
    print("=" * 50)
    
    # Check if we have a test image
    test_images = [
        "uploads/test_form.jpg",
        "uploads/test_form.png", 
        "uploads/sample_form.jpg",
        "uploads/sample_form.png"
    ]
    
    test_image_path = None
    for img_path in test_images:
        if os.path.exists(img_path):
            test_image_path = img_path
            break
    
    if not test_image_path:
        print("❌ No test image found. Please upload a form image first.")
        print("📁 Looking for images in: uploads/")
        print("💡 Upload a form image through the frontend, then run this test.")
        return False
    
    print(f"📸 Using test image: {test_image_path}")
    
    # Create mock data
    mock_coordinates = create_mock_coordinates()
    mock_schema = create_mock_schema()
    
    print(f"📋 Mock coordinates: {len(mock_coordinates)} fields")
    print(f"📝 Mock schema: {len(mock_schema)} fields")
    
    # Initialize image generator
    try:
        generator = FormImageGenerator(test_image_path)
        print("✅ Image generator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize image generator: {e}")
        return False
    
    # Generate filled image
    output_path = "uploads/test_filled_form.jpg"
    try:
        print("\n🎨 Generating filled form...")
        result_path = generator.generate_filled_image_with_coordinates(
            mock_schema, 
            mock_coordinates, 
            output_path
        )
        print(f"✅ Generated filled form: {result_path}")
        
        # Check if file was created
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"📁 File size: {file_size:,} bytes")
            print(f"🔗 View at: http://localhost:5001/get_image/test_filled_form.jpg")
            return True
        else:
            print("❌ Output file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Failed to generate image: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Fill.ai Image Generation Test")
    print("=" * 40)
    
    # Change to backend directory
    os.chdir('/Users/asfawy/fill.ai/backend')
    
    # Run the test
    success = test_image_generation()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📸 Check the generated image to see the last name adjustment")
    else:
        print("\n❌ Test failed. Check the error messages above.")

if __name__ == "__main__":
    main()
