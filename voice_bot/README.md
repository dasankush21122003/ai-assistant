# Intelligent Voice Bot for Customer Interaction

A Python-based voice bot that handles customer queries using AI technologies including Natural Language Processing (NLP), Speech-to-Text, and Text-to-Speech systems.

## Features

### Core Features
- **Speech-to-Text Conversion**: Converts user voice input to text using Google Cloud Speech-to-Text API
- **Natural Language Understanding**: Recognizes user intents and extracts entities from queries
- **Response Generation**: Generates contextual responses based on recognized intents
- **Text-to-Speech Conversion**: Converts bot responses to natural-sounding speech using Google Cloud Text-to-Speech API
- **Audio Recording**: Captures and processes voice input with built-in audio utilities

### Supported Intents
- **Greeting**: Welcomes users and starts conversations
- **Product Information**: Handles product-related queries
- **Order Status**: Provides order tracking and status updates
- **Account Management**: Assists with account-related issues
- **Support**: Handles customer support requests
- **Farewell**: Politely ends conversations

## Project Structure

```
voice_bot/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration and settings
├── modules/
│   ├── __init__.py
│   ├── speech_to_text.py    # Google Cloud STT integration
│   ├── text_to_speech.py    # Google Cloud TTS integration
│   ├── intent_recognizer.py # NLP intent recognition
│   ├── response_generator.py # Response generation logic
│   └── audio_recorder.py    # Audio recording utilities
├── data/
│   └── audio/               # Stored audio files
├── tests/                   # Unit tests (future)
├── main.py                  # Main voice bot application
├── demo.py                  # Demo script (no API required)
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with:
  - Speech-to-Text API enabled
  - Text-to-Speech API enabled
  - Service account with appropriate permissions
- Microphone (for voice input)
- Speakers or headphones (for audio output)

## Installation

### 1. Clone or Download the Project

```bash
cd voice_bot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API
4. Create a service account:
   - Navigate to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Grant roles: "Cloud Speech Client" and "Cloud Text-to-Speech Client"
   - Create and download the JSON key file

5. Save the credentials file in a secure location

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update the following:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
```

## Usage

### Option 1: Run Demo (No API Required)

Test the bot's NLP capabilities without Google Cloud or audio hardware:

```bash
python demo.py
```

This will show you:
- Intent recognition examples
- Response generation examples
- Conversation flow simulation
- Interactive text-based chat

### Option 2: Text-Only Mode

Run the bot with text input/output (requires Google Cloud credentials):

```bash
python main.py
```

Select option 2 for "Text-Only Session"

### Option 3: Full Voice Mode

Run the complete voice bot with audio input/output:

```bash
python main.py
```

Select option 1 for "Interactive Voice Session"

**Note**: Requires:
- Configured Google Cloud credentials
- Working microphone
- Working speakers/headphones

## Configuration

### Audio Settings

Edit `config/settings.py` to customize:

```python
# Audio Configuration
SAMPLE_RATE = 16000      # Audio sample rate in Hz
AUDIO_CHANNELS = 1       # Mono (1) or Stereo (2)
CHUNK_SIZE = 1024        # Audio chunk size for recording

# Language Settings
LANGUAGE_CODE = 'en-US'  # Language for STT and TTS
VOICE_NAME = 'en-US-Standard-A'  # Google Cloud voice name
```

### Intent Recognition

Add or modify intents in `config/settings.py`:

```python
INTENT_KEYWORDS = {
    'greeting': ['hello', 'hi', 'hey'],
    'your_custom_intent': ['keyword1', 'keyword2']
}

RESPONSE_TEMPLATES = {
    'your_custom_intent': [
        "Response template 1",
        "Response template 2"
    ]
}
```

## API Integration

### Google Cloud Speech-to-Text

The bot uses Google Cloud Speech-to-Text API for transcription:
- Automatic punctuation
- Real-time and batch processing
- Support for multiple languages

**Pricing**: Check [Google Cloud Pricing](https://cloud.google.com/speech-to-text/pricing)

### Google Cloud Text-to-Speech

The bot uses Google Cloud Text-to-Speech API for voice synthesis:
- Natural-sounding voices
- Customizable pitch and speaking rate
- Support for SSML

**Pricing**: Check [Google Cloud Pricing](https://cloud.google.com/text-to-speech/pricing)

## Development

### Testing Individual Modules

Each module can be tested independently:

```bash
# Test Speech-to-Text
python -m modules.speech_to_text

# Test Text-to-Speech
python -m modules.text_to_speech

# Test Intent Recognition
python -m modules.intent_recognizer

# Test Response Generation
python -m modules.response_generator
```

### Adding New Features

#### 1. Add New Intent

Edit `config/settings.py`:

```python
INTENT_KEYWORDS = {
    # ... existing intents ...
    'refund': ['refund', 'return', 'money back', 'cancel order']
}

RESPONSE_TEMPLATES = {
    # ... existing responses ...
    'refund': [
        "I can help you with a refund. Let me check the refund policy.",
        "I understand you want a refund. Can you provide your order number?"
    ]
}
```

#### 2. Integrate Backend/Database

Create a new module `modules/database.py`:

```python
class Database:
    def get_order_status(self, order_id):
        # Query your database
        pass

    def get_product_info(self, product_name):
        # Query your database
        pass
```

Update `response_generator.py` to use the database:

```python
from modules.database import Database

class ResponseGenerator:
    def __init__(self):
        self.db = Database()

    def generate_response(self, intent, entities):
        if intent == 'order_status' and 'numbers' in entities:
            order_id = entities['numbers'][0]
            status = self.db.get_order_status(order_id)
            return f"Your order {order_id} is {status}"
```

#### 3. Add OpenAI GPT Integration

Install OpenAI package:

```bash
pip install openai
```

Update `modules/response_generator.py`:

```python
import openai

class AdvancedResponseGenerator(ResponseGenerator):
    def __init__(self, openai_api_key):
        super().__init__()
        openai.api_key = openai_api_key

    def generate_response_ai(self, user_query):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful customer service assistant."},
                {"role": "user", "content": user_query}
            ]
        )
        return response.choices[0].message.content
```

## Troubleshooting

### Common Issues

**1. "Google credentials file not found"**
- Ensure the path in `.env` points to your actual credentials file
- Use absolute path instead of relative path

**2. "pyaudio installation failed"**

On macOS:
```bash
brew install portaudio
pip install pyaudio
```

On Ubuntu/Debian:
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

On Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

**3. "No audio input device found"**
- Check your microphone is properly connected
- Verify microphone permissions in system settings

**4. "API quota exceeded"**
- Check your Google Cloud billing and quotas
- Consider implementing rate limiting

## Future Enhancements

### Planned Features
- [ ] ML-based intent recognition using Transformers
- [ ] Multi-language support
- [ ] Real-time streaming conversations
- [ ] Analytics dashboard
- [ ] Database integration for dynamic data
- [ ] Web interface (Flask/FastAPI)
- [ ] Sentiment analysis
- [ ] Voice authentication
- [ ] Context persistence across sessions
- [ ] Integration with CRM systems

### Advanced NLP

Replace keyword-based intent recognition with ML models:

```python
from transformers import pipeline

classifier = pipeline("text-classification",
                     model="distilbert-base-uncased-finetuned-sst-2-english")

def recognize_intent_ml(text):
    result = classifier(text)
    return result[0]['label'], result[0]['score']
```

### Real-Time Streaming

Implement streaming speech recognition:

```python
def streaming_conversation():
    with audio_recorder.streaming_audio() as stream:
        for audio_chunk in stream:
            text = stt.transcribe_streaming(audio_chunk)
            if text:
                # Process and respond immediately
                process_and_respond(text)
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is created for educational purposes as part of an AI internship project.

## Resources

- [Google Cloud Speech-to-Text Documentation](https://cloud.google.com/speech-to-text/docs)
- [Google Cloud Text-to-Speech Documentation](https://cloud.google.com/text-to-speech/docs)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/)

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the demo script for examples
3. Check module documentation in source files

## Authors

AI Intern Project - Voice Bot Development

---

**Version**: 1.0.0
**Last Updated**: November 2024
