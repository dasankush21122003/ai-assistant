"""
Flask Web API for Voice Bot
Provides REST endpoints for the voice bot functionality
"""
import os
import sys
import base64
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.intent_recognizer import IntentRecognizer
from modules.response_generator import ResponseGenerator
from config.settings import Config

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize bot components
try:
    Config.validate()
    stt = SpeechToText()
    tts = TextToSpeech()
    intent_recognizer = IntentRecognizer()
    response_generator = ResponseGenerator()
    print("Voice Bot API initialized successfully!")
except Exception as e:
    print(f"Error initializing Voice Bot API: {str(e)}")
    stt = None
    tts = None
    intent_recognizer = None
    response_generator = None

# Create necessary directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'audio')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm', 'ogg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot_name': Config.BOT_NAME if Config else 'Voice Bot',
        'services': {
            'stt': stt is not None,
            'tts': tts is not None,
            'intent_recognizer': intent_recognizer is not None,
            'response_generator': response_generator is not None
        }
    })


@app.route('/api/process-text', methods=['POST'])
def process_text():
    """
    Process text input and return bot response

    Request body:
    {
        "text": "user input text"
    }

    Response:
    {
        "user_text": "...",
        "intent": "...",
        "confidence": 0.95,
        "entities": {...},
        "response_text": "...",
        "response_audio_base64": "..."
    }
    """
    try:
        data = request.get_json()
        user_text = data.get('text', '').strip()

        if not user_text:
            return jsonify({'error': 'No text provided'}), 400

        # Analyze intent
        analysis = intent_recognizer.analyze_query(user_text)

        # Generate response
        response_text = response_generator.generate_response(
            analysis['intent'],
            analysis['entities'],
            analysis['context']
        )

        # Generate audio response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file = os.path.join(OUTPUT_FOLDER, f'response_{timestamp}.mp3')
        tts.synthesize_speech(response_text, audio_file)

        # Read audio file and encode to base64
        with open(audio_file, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'user_text': user_text,
            'intent': analysis['intent'],
            'confidence': analysis['confidence'],
            'entities': analysis['entities'],
            'response_text': response_text,
            'response_audio_base64': audio_base64
        })

    except Exception as e:
        print(f"Error processing text: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-audio', methods=['POST'])
def process_audio():
    """
    Process audio input and return bot response

    Expects multipart/form-data with 'audio' file

    Response:
    {
        "user_text": "...",
        "intent": "...",
        "confidence": 0.95,
        "entities": {...},
        "response_text": "...",
        "response_audio_base64": "..."
    }
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400

        if not allowed_file(audio_file.filename):
            return jsonify({'error': 'Invalid file format'}), 400

        # Save uploaded audio file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(f'input_{timestamp}.wav')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        audio_file.save(filepath)

        # Transcribe audio
        user_text = stt.transcribe_audio_file(filepath)

        if not user_text:
            return jsonify({'error': 'Failed to transcribe audio'}), 500

        # Analyze intent
        analysis = intent_recognizer.analyze_query(user_text)

        # Generate response
        response_text = response_generator.generate_response(
            analysis['intent'],
            analysis['entities'],
            analysis['context']
        )

        # Generate audio response
        response_audio_file = os.path.join(OUTPUT_FOLDER, f'response_{timestamp}.mp3')
        tts.synthesize_speech(response_text, response_audio_file)

        # Read audio file and encode to base64
        with open(response_audio_file, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'user_text': user_text,
            'intent': analysis['intent'],
            'confidence': analysis['confidence'],
            'entities': analysis['entities'],
            'response_text': response_text,
            'response_audio_base64': audio_base64
        })

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/greeting', methods=['GET'])
def get_greeting():
    """Get the greeting message"""
    try:
        greeting = Config.GREETING_MESSAGE

        # Generate audio greeting
        audio_file = os.path.join(OUTPUT_FOLDER, 'greeting.mp3')
        tts.synthesize_speech(greeting, audio_file)

        # Read audio file and encode to base64
        with open(audio_file, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'text': greeting,
            'audio_base64': audio_base64
        })

    except Exception as e:
        print(f"Error getting greeting: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Voice Bot Web API Starting...")
    print("=" * 60)
    print(f"\nBot Name: {Config.BOT_NAME if Config else 'Voice Bot'}")
    print("API will be available at: http://localhost:5000")
    print("Frontend will be available at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
