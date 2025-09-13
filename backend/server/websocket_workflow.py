import os
import json
import time
import threading
import sys
import base64
sys.path.append('.')

from .practice import extract_and_generate_schema
from .human_conversation import HumanConversationAI
from .image_generator import FormImageGenerator
from .enhanced_coordinate_extractor import CoordinateExtractor
from openai import OpenAI
from dotenv import load_dotenv
import pyttsx3
import speech_recognition as sr
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

class WebSocketSpeechFormFiller:
    def __init__(self, socketio_emitter=None):
        """Initialize the WebSocket-enabled form filler"""
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.socketio_emitter = socketio_emitter
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        print("🎤 Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone calibrated!")
        
        # Initialize ElevenLabs for TTS
        self.elevenlabs_client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY")
        )
        print("✅ ElevenLabs initialized for TTS")
        
        # Initialize coordinate extractor with Azure credentials
        endpoint = os.getenv('AZURE_ENDPOINT', 'https://aiformfilling-doc-ai.cognitiveservices.azure.com/')
        key = os.getenv('AZURE_KEY')
        if not key:
            raise ValueError("AZURE_KEY not found in environment variables")
        
        self.coordinate_extractor = CoordinateExtractor(endpoint, key)
        print("✅ Azure coordinate extractor initialized")
        
        # Conversation state
        self.current_field_index = 0
        self.required_fields = []
        self.schema = None
        self.is_conversation_active = False
        
        # Initialize human conversation AI
        self.human_ai = HumanConversationAI()
        self.original_image_path = None
        self.is_listening = False
        self.field_coordinates = {}  # Store Azure coordinates
        
    def setup_tts(self):
        """Configure text-to-speech settings"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to use a female voice if available
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
    def emit(self, event_type, data):
        """Emit data to frontend via WebSocket"""
        if self.socketio_emitter:
            self.socketio_emitter(event_type, data)
    
    def speak(self, text):
        """Convert text to speech using ElevenLabs (exactly like real_workflow)"""
        print(f"🤖 Speaking: {text}")
        self.emit('speech_text', {'text': text, 'is_ai': True})
        
        try:
            # Use ElevenLabs exactly like real_workflow
            audio_stream = self.elevenlabs_client.text_to_speech.stream(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2"
            )
            
            # Play the streamed audio locally
            stream(audio_stream)
            print("✅ ElevenLabs speech completed")
            
        except Exception as e:
            print(f"❌ ElevenLabs error: {e}, falling back to pyttsx3")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            print("✅ pyttsx3 speech completed")
    
    def listen(self, timeout=10):
        """Listen for user speech input (exactly like real_workflow)"""
        print(f"🎤 Listening... (timeout: {timeout}s)")
        
        try:
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            # Recognize speech using Google's service
            text = self.recognizer.recognize_google(audio)
            print(f"👤 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ Timeout waiting for speech input")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def get_user_input_speech(self, question, field_type="text"):
        """Get user input through speech with fallback (exactly like real_workflow)"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            # Speak the question
            self.speak(question)
            
            # Try to get speech input
            response = self.listen(timeout=15)
            
            if response:
                # Validate response based on field type
                if self.validate_response(response, field_type):
                    return response
                else:
                    self.speak("I didn't understand that. Please try again.")
            else:
                if attempt < max_attempts - 1:
                    self.speak("I didn't catch that. Please speak again.")
                else:
                    # Fallback - skip this field
                    self.speak("Skipping this field. Let's continue.")
                    return None
        
        return None
    
    def validate_response(self, response, field_type):
        """Basic validation for different field types (exactly like real_workflow)"""
        if field_type == "email":
            return "@" in response and "." in response
        elif field_type == "phone":
            return any(char.isdigit() for char in response)
        elif field_type == "date":
            return any(char.isdigit() for char in response)
        else:
            return len(response.strip()) > 0
    
    def start_conversation(self):
        """Start the conversational form filling process"""
        if not self.required_fields:
            self.speak("No fields to fill out. Let me analyze the form first.")
            return False
        
        self.is_conversation_active = True
        self.current_field_index = 0
        
        self.speak(f"Great! I found {len(self.required_fields)} fields to fill out. Let's start with the first question.")
        
        # Start with the first field
        self.ask_next_question()
        return True
    
    def ask_next_question(self):
        """Ask the next question in the conversation (exactly like real_workflow)"""
        if not self.is_conversation_active or self.current_field_index >= len(self.required_fields):
            self.finish_conversation()
            return
        
        field = self.required_fields[self.current_field_index]
        
        print(f"\n--- Field {self.current_field_index + 1}/{len(self.required_fields)} ---")
        print(f"Label: {field.get('label', 'N/A')}")
        print(f"Type: {field.get('type', 'N/A')}")
        
        if field.get('options'):
            print(f"Options: {', '.join(field.get('options', []))}")
        
        # Generate conversational question using OpenAI (exactly like real_workflow)
        try:
            # Use human conversation AI for questions
            question = self.human_ai.get_field_question(field, field.get('type', 'text'))
            
            # Add progress and personality
            progress = f"Question {self.current_field_index + 1} of {len(self.required_fields)}: "
            full_question = f"{progress}{question}"
            
            # Add encouragement if appropriate
            if self.human_ai.should_encourage():
                encouragement = self.human_ai.get_encouragement()
                full_question = f"{encouragement} {full_question}"
                self.human_ai.encouragement_given += 1
            
            # Add joke if appropriate
            if self.human_ai.should_tell_joke():
                joke = self.human_ai.get_joke(field.get('type', 'text'))
                full_question = f"{full_question} {joke}"
                self.human_ai.jokes_told += 1
            
            # Add progress comment
            progress_comment = self.human_ai.get_progress_comment()
            full_question = f"{full_question} {progress_comment}"
            
            # Update field count
            self.human_ai.field_count = self.current_field_index + 1
            self.human_ai.total_fields = len(self.required_fields)
            
            # Old field_prompt code (commented out)
            field_prompt = (
                f"Ask the user for the following field in a conversational way:\n"
                f"Label: {field.get('label','')}\n"
                f"Type: {field.get('type','')}\n"
                f"Options: {', '.join(field.get('options', [])) if field.get('options') else 'N/A'}\n"
                f"Accessibility: {field.get('accessibility','')}\n"
                f"Respond with only the question, keep it short and friendly."
            )
            
            ai_question = self.client.chat.completions.create(
                model='gpt-4-1106-preview',
                messages=[{
                    'role': 'system',
                    'content': "You are a helpful assistant guiding a user through filling out a digital form. Ask one required field at a time in a conversational way. Keep questions short and clear."
                }, {
                    'role': 'user',
                    'content': field_prompt
                }],
                max_tokens=100,
                temperature=0.3
            ).choices[0].message.content
            
            # Add progress indicator
            progress = f"Question {self.current_field_index + 1} of {len(self.required_fields)}: "
            full_question = f"{progress}{ai_question}"
            
            # Emit the question to frontend
            self.emit('conversation_question', {
                'question': full_question,
                'field': field,
                'progress': {
                    'current': self.current_field_index + 1,
                    'total': len(self.required_fields)
                }
            })
            
            # Get user input through speech (exactly like real_workflow)
            user_input = self.get_user_input_speech(full_question, field.get('type', 'text'))
            
            if user_input:
                field['value'] = user_input
                # Confirm the input
                self.speak(f"Got it! {field.get('label')}: {user_input}")
                
                # Emit confirmation to frontend
                self.emit('conversation_answer', {
                    'field': field,
                    'answer': user_input,
                    'confirmed': True
                })
            else:
                self.speak("Skipping this field. Let's continue.")
                
                # Emit skip to frontend
                self.emit('conversation_answer', {
                    'field': field,
                    'answer': '',
                    'confirmed': False
                })
            
            # Move to next field
            self.current_field_index += 1
            
            # Wait a moment before asking next question
            time.sleep(1)
            
            # Ask next question or finish
            if self.current_field_index < len(self.required_fields):
                self.ask_next_question()
            else:
                self.finish_conversation()
                
        except Exception as e:
            print(f"Error processing field {field.get('label')} with speech: {e}")
            # Skip this field and continue
            self.current_field_index += 1
            if self.current_field_index < len(self.required_fields):
                self.ask_next_question()
            else:
                self.finish_conversation()
    
    def finish_conversation(self):
        """Finish the conversation and generate the filled form"""
        self.is_conversation_active = False
        
        # Initialize human conversation AI
        self.human_ai = HumanConversationAI()
        
        # Count filled fields
        filled_fields = [f for f in self.required_fields if f.get('value')]
        
        # Use human-like completion message
        completion_message = self.human_ai.get_completion_message()
        self.speak(completion_message)
        
        # Add progress comment
        progress_comment = self.human_ai.get_progress_comment()
        self.speak(progress_comment)
        
        # Add final encouragement
        if self.human_ai.should_encourage():
            encouragement = self.human_ai.get_encouragement()
            self.speak(encouragement)
        
        self.speak("Now let me generate your completed form!")
        
        # Emit completion to frontend
        self.emit('conversation_complete', {
            'filled_fields': filled_fields,
            'total_fields': len(self.required_fields)
        })
        
        # Generate the filled form
        self.generate_filled_form()
    
    def generate_filled_form(self):
        """Generate the filled form image using Azure coordinates"""
        try:
            self.emit('progress_update', {
                'step': 'generating',
                'message': '🎨 Generating your completed form with precise positioning...',
                'progress': 90
            })
            
            # Initialize image generator with the image path
            image_generator = FormImageGenerator(self.original_image_path)
            
            # Use the Azure coordinates for precise positioning
            if self.field_coordinates:
                print(f"🎯 Using {len(self.field_coordinates)} Azure coordinates for precise positioning")
                filled_image_path = image_generator.generate_filled_image_with_coordinates(
                    self.schema, 
                    self.field_coordinates
                )
            else:
                print("⚠️ No Azure coordinates available, using estimated positioning")
                filled_image_path = image_generator.generate_filled_image(self.schema)
            
            if filled_image_path and os.path.exists(filled_image_path):
                print(f"✅ Generated form image: {filled_image_path}")
                
                # Convert to absolute path for serving
                abs_path = os.path.abspath(filled_image_path)
                print(f"✅ Absolute path: {abs_path}")
                
                self.emit('progress_update', {
                    'step': 'completed',
                    'message': '✅ Form completed successfully!',
                    'progress': 100
                })
                
                # Emit the generated image with both path and base64
                try:
                    with open(filled_image_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                    
                    self.emit('generated_image', {
                        'image': image_data,
                        'image_path': abs_path,
                        'description': 'Your completed form'
                    })
                except Exception as e:
                    print(f"❌ Error encoding image: {e}")
                    # Fallback to just path
                    self.emit('generated_image', {
                        'image_path': abs_path,
                        'description': 'Your completed form'
                    })
                
                self.speak("Perfect! Your form is ready. You can download it now.")
                
                return {
                    'success': True,
                    'output_image': filled_image_path,
                    'schema': self.schema,
                    'filled_fields': [f for f in self.required_fields if f.get('value')]
                }
            else:
                raise Exception("Failed to generate filled form")
                
        except Exception as e:
            print(f"❌ Error generating form: {e}")
            self.emit('error', {'message': f'Error generating form: {str(e)}'})
            return {'success': False, 'error': str(e)}
    
    def run_workflow(self, image_path):
        """Run the complete form filling workflow with Azure coordinates"""
        try:
            self.original_image_path = image_path
            
            self.emit('progress_update', {
                'step': 'starting',
                'message': '🚀 Starting Fill.ai workflow...',
                'progress': 5
            })
            
            # Step 1: Extract form structure
            self.emit('progress_update', {
                'step': 'extracting',
                'message': '📋 Step 1: Analyzing your form with Azure OCR...',
                'progress': 20
            })
            
            schema_result = extract_and_generate_schema(image_path)
            if not schema_result or not schema_result.get('success'):
                raise Exception("Failed to extract form schema")
            
            self.schema = schema_result['schema']
            
            # Get required fields
            fields = []
            if "fields" in self.schema:
                fields = self.schema["fields"]
            elif "sections" in self.schema:
                for section in self.schema["sections"]:
                    fields.extend(section.get("fields", []))
            
            self.required_fields = [f for f in fields if f.get('required')]
            
            self.emit('progress_update', {
                'step': 'extracting',
                'message': f'✅ Found {len(self.required_fields)} fields to fill out!',
                'progress': 30
            })
            
            # Step 2: Extract field coordinates using Azure
            self.emit('progress_update', {
                'step': 'coordinates',
                'message': '📐 Step 2: Extracting precise field coordinates with Azure...',
                'progress': 40
            })
            
            print("🔍 Extracting field coordinates with Azure Document Intelligence...")
            self.field_coordinates = self.coordinate_extractor.get_coordinate_mapping(image_path)
            
            if self.field_coordinates:
                print(f"✅ Extracted {len(self.field_coordinates)} field coordinates from Azure")
                self.emit('progress_update', {
                    'step': 'coordinates',
                    'message': f'✅ Found {len(self.field_coordinates)} field positions!',
                    'progress': 50
                })
            else:
                print("⚠️ No coordinates extracted, will use estimated positioning")
                self.emit('progress_update', {
                    'step': 'coordinates',
                    'message': '⚠️ Using estimated positioning',
                    'progress': 50
                })
            
            # Step 3: Start conversation
            self.emit('progress_update', {
                'step': 'conversation',
                'message': '💬 Step 3: Starting conversation...',
                'progress': 60
            })
            
            # Welcome message
            self.speak("Welcome to Fill.ai! I'll help you turn this PDF form into a conversation. Let me ask you questions one by one to fill out the form.")
            
            # Start the conversation
            self.start_conversation()
            
            return {
                'success': True,
                'schema': self.schema,
                'coordinates': self.field_coordinates,
                'fields': self.required_fields,
                'conversation_started': True
            }
                
        except Exception as e:
            self.emit('error', {'message': f'Workflow error: {str(e)}'})
            return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    # Test the workflow
    filler = WebSocketSpeechFormFiller()
    result = filler.run_workflow("sample_data/simple-job-application-form-27d287c8e2b97cd3f175c12ef67426b2-classic.png")
    print("Result:", result)
