import os
import json
import subprocess
import platform
from PIL import Image
from image_generator import FormImageGenerator


class PositionTester:
    """
    A utility class to test form field positioning by generating filled forms
    and opening them with the default image viewer.
    """
    
    def __init__(self, sample_data_dir="../sample_data"):
        """
        Initialize the position tester.
        
        Args:
            sample_data_dir (str): Path to the directory containing sample data
        """
        self.sample_data_dir = sample_data_dir
        self.form_data_path = os.path.join(sample_data_dir, "form_data.json")
        self.position_data_path = os.path.join(sample_data_dir, "position_data.json")
        self.input_form_path = os.path.join(sample_data_dir, "test_form.jpg")
        
    def load_json_data(self, file_path):
        """Load JSON data from a file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON from {file_path}: {e}")
            return None
    
    def open_image_with_default_viewer(self, image_path):
        """
        Open an image with the default system image viewer.
        
        Args:
            image_path (str): Path to the image file
        """
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(["open", image_path], check=True)
            elif system == "Windows":
                subprocess.run(["start", image_path], shell=True, check=True)
            elif system == "Linux":
                subprocess.run(["xdg-open", image_path], check=True)
            else:
                print(f"❌ Unsupported operating system: {system}")
                return False
                
            print(f"✅ Opened {image_path} with default image viewer")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to open image: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ Command not found for opening images on {system}")
            return False
    
    def test_position_accuracy(self, output_name="test_filled_form.jpg"):
        """
        Test the accuracy of field positioning by generating a filled form
        and opening it for visual inspection.
        
        Args:
            output_name (str): Name of the output file (will overwrite if exists)
        """
        print("🧪 Starting position accuracy test...")
        
        # Load the form data
        form_data = self.load_json_data(self.form_data_path)
        if not form_data:
            return False
        
        # Load the position data
        position_data = self.load_json_data(self.position_data_path)
        if not position_data:
            return False
        
        # Check if input form exists
        if not os.path.exists(self.input_form_path):
            print(f"❌ Input form not found: {self.input_form_path}")
            return False
        
        print(f"📋 Loaded {len(form_data.get('fields', []))} form fields")
        print(f"📐 Loaded {len(position_data)} position coordinates")
        
        # Initialize the form image generator
        try:
            generator = FormImageGenerator(self.input_form_path)
        except Exception as e:
            print(f"❌ Failed to initialize FormImageGenerator: {e}")
            return False
        
        # Generate the filled image with coordinates
        output_path = os.path.join(self.sample_data_dir, output_name)
        
        try:
            result_path = generator.generate_filled_image_with_coordinates(
                form_data, 
                position_data, 
                output_path
            )
            print(f"✅ Generated filled form: {result_path}")
            
            # Open with default viewer
            self.open_image_with_default_viewer(result_path)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate filled image: {e}")
            return False
    
    def test_multiple_variations(self):
        """
        Test multiple variations of form filling to see how different
        data values affect positioning.
        """
        print("🔄 Testing multiple form variations...")
        
        # Load base form data
        form_data = self.load_json_data(self.form_data_path)
        position_data = self.load_json_data(self.position_data_path)
        
        if not form_data or not position_data:
            return False
        
        # Create test variations
        test_variations = [
            {
                "name": "original_data",
                "modifications": {}
            },
            {
                "name": "long_names",
                "modifications": {
                    "family_name": "VeryLongFamilyNameThatMightOverflow",
                    "given_name": "ExtremelyLongFirstNameExample",
                    "middle_name": "UnnecessarilyLongMiddleName"
                }
            },
            {
                "name": "short_names",
                "modifications": {
                    "family_name": "Li",
                    "given_name": "Jo",
                    "middle_name": "A"
                }
            },
            {
                "name": "special_characters",
                "modifications": {
                    "family_name": "O'Connor-Smith",
                    "given_name": "José",
                    "middle_name": "María"
                }
            }
        ]
        
        generator = FormImageGenerator(self.input_form_path)
        
        for variation in test_variations:
            print(f"\n🔬 Testing variation: {variation['name']}")
            
            # Create modified form data
            modified_form_data = json.loads(json.dumps(form_data))  # Deep copy
            
            # Apply modifications
            for field in modified_form_data.get('fields', []):
                field_key = self.get_field_key(field['label'])
                if field_key in variation['modifications']:
                    field['value'] = variation['modifications'][field_key]
            
            # Generate image
            output_name = f"test_{variation['name']}.jpg"
            output_path = os.path.join(self.sample_data_dir, output_name)
            
            try:
                result_path = generator.generate_filled_image_with_coordinates(
                    modified_form_data,
                    position_data,
                    output_path
                )
                print(f"  ✅ Generated: {result_path}")
                
                # Optional: Open each variation (comment out if too many windows)
                # self.open_image_with_default_viewer(result_path)
                
            except Exception as e:
                print(f"  ❌ Failed to generate {variation['name']}: {e}")
        
        print(f"\n🎯 Generated test variations in: {self.sample_data_dir}")
        return True
    
    def get_field_key(self, label):
        """
        Convert a field label to a key that matches position_data keys.
        
        Args:
            label (str): The field label
            
        Returns:
            str: The corresponding key for position_data
        """
        label_lower = label.lower()
        
        # Mapping of common labels to position data keys
        mappings = {
            'family name (last name)': 'family_name',
            'given name (first name)': 'given_name',
            'middle name': 'middle_name',
            'alien registration number (a-number)': 'alien_registration_number',
            'uscis online account number': 'uscis_online_account_number'
        }
        
        return mappings.get(label_lower, label_lower.replace(' ', '_').replace('(', '').replace(')', ''))
    
    def compare_positions(self):
        """
        Generate a comparison image showing field positions with labels.
        """
        print("📊 Generating position comparison...")
        
        position_data = self.load_json_data(self.position_data_path)
        if not position_data:
            return False
        
        # Create a copy of the original image for annotation
        original_image = Image.open(self.input_form_path)
        comparison_path = os.path.join(self.sample_data_dir, "position_comparison.jpg")
        
        # Use the generator to create an annotated version
        generator = FormImageGenerator(self.input_form_path)
        
        # Create empty form data with just labels for positioning
        label_data = {
            "fields": [
                {"label": key.replace('_', ' ').title(), "value": f"[{key}]", "type": "text"}
                for key in position_data.keys()
            ]
        }
        
        try:
            result_path = generator.generate_filled_image_with_coordinates(
                label_data,
                position_data,
                comparison_path
            )
            print(f"✅ Generated position comparison: {result_path}")
            self.open_image_with_default_viewer(result_path)
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate comparison: {e}")
            return False


def main():
    """
    Main function to run position tests.
    """
    print("🚀 Form Position Tester")
    print("=" * 50)
    
    # Initialize tester
    tester = PositionTester()
    
    # Run basic position test
    print("\n1️⃣ Running basic position accuracy test...")
    tester.test_position_accuracy("test_basic_positioning.jpg")
    
    # Wait for user input before continuing
    input("\nPress Enter to continue with position comparison...")
    
    # Run position comparison
    print("\n2️⃣ Generating position comparison...")
    tester.compare_positions()
    
    # Wait for user input before continuing
    input("\nPress Enter to continue with multiple variations test...")
    
    # Run multiple variations test
    print("\n3️⃣ Testing multiple data variations...")
    tester.test_multiple_variations()
    
    print("\n✅ All tests completed!")
    print(f"📁 Check the sample_data directory for generated images.")


if __name__ == "__main__":
    main()