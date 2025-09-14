import os
import json
import base64
import threading
import time
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
sys.path.append('server')

from server.websocket_workflow import WebSocketSpeechFormFiller

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fill-ai-secret-key'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class WebSocketFormFiller:
    def __init__(self, socketio):
        self.socketio = socketio
        self.form_filler = None
        self.current_session = None
        
    def emit_message(self, message_type, data):
        """Emit a message to the frontend"""
        self.socketio.emit(message_type, data)
        
    def emit_progress(self, step, message, progress=None):
        """Emit progress update"""
        data = {
            'step': step,
            'message': message,
            'progress': progress,
            'timestamp': time.time()
        }
        self.emit_message('progress_update', data)
        
    def emit_speech(self, text, is_ai=True):
        """Emit speech text to be displayed"""
        data = {
            'text': text,
            'is_ai': is_ai,
            'timestamp': time.time()
        }
        self.emit_message('speech_text', data)
        
    def emit_image(self, image_path, description=""):
        """Emit generated image"""
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            data = {
                'image': image_data,
                'description': description,
                'timestamp': time.time()
            }
            self.emit_message('generated_image', data)
        except Exception as e:
            self.emit_message('error', {'message': f'Failed to load image: {str(e)}'})
    
    def process_form_workflow(self, file_path, session_id):
        """Process the form workflow with real-time updates"""
        try:
            self.current_session = session_id
            self.emit_progress('starting', 'Initializing Fill.ai...', 0)
            
            # Initialize the WebSocket form filler
            self.form_filler = WebSocketSpeechFormFiller(socketio_emitter=self.emit_message)
            
            # Start the workflow
            self.emit_speech("Welcome to Fill.ai! I'll help you turn PDF forms into conversations.", is_ai=True)
            self.emit_progress('starting', 'Starting form processing workflow...', 5)
            
            # Run the actual workflow
            result = self.form_filler.run_workflow(file_path)
            
            if result and result.get('success'):
                # Don't emit completion here - let the conversation handle it
                pass
            else:
                self.emit_message('error', {'message': 'Form processing failed'})
                
        except Exception as e:
            self.emit_message('error', {'message': f'Error processing form: {str(e)}'})
        finally:
            self.current_session = None

# Global instance
ws_form_filler = WebSocketFormFiller(socketio)

@app.route('/')
def index():
    return jsonify({'message': 'Fill.ai Backend API', 'status': 'running'})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'file_path': file_path
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/extract_schema', methods=['POST'])
def extract_schema():
    """Extract JSON schema from uploaded form image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save the uploaded file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Import the schema extraction function
            from server.practice import extract_and_generate_schema
            
            # Extract schema using your existing function
            schema_result = extract_and_generate_schema(file_path)
            
            if schema_result.get('success'):
                return jsonify({
                    'success': True,
                    'schema': schema_result['schema'],
                    'fields': schema_result['fields'],
                    'form_title': schema_result.get('form_title', 'Unknown Form'),
                    'raw_text': schema_result['raw_text'],
                    'processing_time': {
                        'azure_time': schema_result['azure_time'],
                        'openai_time': schema_result['openai_time']
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': schema_result.get('error', 'Schema extraction failed')
                }), 500
        
        return jsonify({'error': 'Invalid file type. Allowed: PDF, PNG, JPG, JPEG'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Schema extraction failed: {str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to Fill.ai backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('start_processing')
def handle_start_processing(data):
    """Start form processing workflow"""
    file_path = data.get('file_path')
    session_id = data.get('session_id', 'default')
    
    if not file_path or not os.path.exists(file_path):
        emit('error', {'message': 'Invalid file path'})
        return
    
    # Start processing in a separate thread
    thread = threading.Thread(
        target=ws_form_filler.process_form_workflow,
        args=(file_path, session_id)
    )
    thread.daemon = True
    thread.start()
    
    emit('processing_started', {'message': 'Form processing started'})

@socketio.on('send_message')
def handle_user_message(data):
    """Handle user message during conversation"""
    message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if ws_form_filler.current_session == session_id and ws_form_filler.form_filler:
        # Process the user's answer
        ws_form_filler.form_filler.process_user_answer(message)
    else:
        emit('error', {'message': 'No active conversation'})

@socketio.on('start_conversation')
def handle_start_conversation(data):
    """Start the conversation manually"""
    session_id = data.get('session_id', 'default')
    
    if ws_form_filler.current_session == session_id and ws_form_filler.form_filler:
        ws_form_filler.form_filler.start_conversation()
    else:
        emit('error', {'message': 'No active form processing'})

if __name__ == '__main__':
    print("🚀 Starting Fill.ai Backend Server...")
    print("📡 WebSocket server running on http://localhost:5001")
    print("🔗 Frontend should connect to: ws://localhost:5001")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)

@app.route('/get_image')
def get_image():
    """Serve generated images"""
    image_path = request.args.get('path')
    if not image_path or not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        return image_data, 200, {
            'Content-Type': 'image/png',
            'Content-Disposition': 'inline'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Fill.ai backend is running'})

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({'message': 'Fill.ai Backend API', 'status': 'running'})

@socketio.on('test')
def handle_test(data):
    """Test WebSocket connection"""
    print(f"Received test message: {data}")
    emit('test_response', {'message': 'Hello from backend!', 'received': data})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected to WebSocket')
    emit('connected', {'message': 'Connected to Fill.ai backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected from WebSocket')
