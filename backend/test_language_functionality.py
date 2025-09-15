#!/usr/bin/env python3
"""
Test script for the multilingual form filling functionality
"""
import os
import sys
sys.path.append('server')

from server.websocket_workflow import WebSocketSpeechFormFiller

def test_language_functionality():
    """Test the language selection and translation features"""
    print("🧪 Testing Language Functionality...")
    
    # Initialize the form filler
    form_filler = WebSocketSpeechFormFiller()
    
    # Test 1: Set language programmatically
    print("\n--- Test 1: Setting language programmatically ---")
    result = form_filler.set_user_language('ukrainian')
    print(f"Ukrainian set: {result}")
    
    result = form_filler.set_user_language('amharic')
    print(f"Amharic set: {result}")
    
    result = form_filler.set_user_language('english')
    print(f"English set: {result}")
    
    # Test 2: Translation functionality
    print("\n--- Test 2: Translation functionality ---")
    
    # Test Ukrainian translation
    form_filler.user_language = 'ukrainian'
    english_text = "What is your full name?"
    ukrainian_text = form_filler.translate_text(english_text, 'English', 'Ukrainian')
    print(f"English: {english_text}")
    print(f"Ukrainian: {ukrainian_text}")
    
    # Test Amharic translation
    form_filler.user_language = 'amharic'
    amharic_text = form_filler.translate_text(english_text, 'English', 'Amharic')
    print(f"Amharic: {amharic_text}")
    
    # Test reverse translation (user response to English)
    sample_response = "ჯონ სმითი"  # Georgian name as test
    english_response = form_filler.translate_user_response_to_english(sample_response)
    print(f"User response: {sample_response}")
    print(f"English translation: {english_response}")
    
    # Test 3: Language availability
    print("\n--- Test 3: Available languages ---")
    for lang_key, lang_info in form_filler.available_languages.items():
        print(f"{lang_key}: {lang_info['name']} ({lang_info['code']})")
    
    print("\n✅ Language functionality test completed!")

if __name__ == "__main__":
    test_language_functionality()