# Voice Bot Setup Guide

Complete step-by-step guide to set up and run the AI Voice Assistant.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Google Cloud Setup](#google-cloud-setup)
4. [OpenAI Setup (Optional)](#openai-setup-optional)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
- **pip** package manager
- **Google Cloud Platform account** (free tier available)
- **OpenAI account** (optional, for AI-powered responses)
- **Microphone** (for voice input)
- **Speakers** (for audio output)

Check Python version:
```bash
python --version
# or
python3 --version
```

---

## Installation

### Step 1: Clone or Navigate to Project

```bash
cd /Users/sayandas/Documents/ai_intern_project_ankush/voice_bot
```

### Step 2: Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If `pyaudio` installation fails on macOS, run:
```bash
brew install portaudio
pip install pyaudio
```

For other issues with pyaudio, see [PYAUDIO_FIX.md](PYAUDIO_FIX.md)

---

## Google Cloud Setup

The voice bot requires Google Cloud Speech-to-Text and Text-to-Speech APIs.

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Create Project**
3. Enter project name (e.g., "voice-bot-project")
4. Click **Create**

### Step 2: Enable Required APIs

1. In Google Cloud Console, go to **APIs & Services > Library**
2. Search for and enable:
   - **Cloud Speech-to-Text API**
   - **Cloud Text-to-Speech API**

### Step 3: Create Service Account

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > Service Account**
3. Enter service account details:
   - Name: `voice-bot-service`
   - Click **Create and Continue**
4. Grant role: **Owner** or **Editor**
5. Click **Continue** then **Done**

### Step 4: Generate Service Account Key

1. Click on the created service account
2. Go to **Keys** tab
3. Click **Add Key > Create New Key**
4. Select **JSON** format
5. Click **Create**
6. Save the downloaded JSON file securely

**Important:** Keep this file secure and never commit it to version control.

### Step 5: Configure Credentials

1. Place the JSON key file in a secure location (e.g., `~/credentials/`)

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Edit `.env` file:
```bash
nano .env
# or use any text editor
```

4. Update the credentials path:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
```

Example:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/Users/sayandas/credentials/voice-bot-key.json
GOOGLE_CLOUD_PROJECT_ID=voice-bot-project
```

---

## OpenAI Setup (Optional)

For AI-powered dynamic responses using GPT-3.5 Turbo.

### Step 1: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the generated key (you won't see it again)

### Step 2: Add to Environment

Edit your `.env` file:
```bash
nano .env
```

Add or uncomment:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

**Note:** If you skip this step, the bot will use template-based responses instead.

---

## Running the Application

You have three options to run the voice bot:

### Option 1: Streamlit Web Interface (Recommended)

The most feature-rich option with analytics dashboard, FAQ manager, and settings.

```bash
streamlit run streamlit_app.py
```

The application will open automatically at `http://localhost:8501`

**Features:**
- Chat with text or voice input
- Analytics Dashboard with real-time metrics
- FAQ Manager for knowledge base
- Settings page for configuration
- Response time tracking

### Option 2: Command Line Interface

Interactive terminal-based interface.

```bash
python main.py
```

Choose from:
1. Interactive Voice Session (requires microphone)
2. Text-Only Session (no audio required)

### Option 3: Flask REST API

For developers who want to build custom frontends.

```bash
python app.py
```

API available at `http://localhost:5000`

**Endpoints:**
- `GET /api/health` - Health check
- `POST /api/process-text` - Process text input
- `POST /api/process-audio` - Process audio file
- `GET /api/greeting` - Get greeting message

---

## Testing

### Test 1: Verify Installation

```bash
python -c "import streamlit, openai; print('All packages installed successfully')"
```

### Test 2: Check Google Cloud Credentials

```bash
python -c "from modules.speech_to_text import SpeechToText; print('Google Cloud configured:', SpeechToText() is not None)"
```

### Test 3: Run Demo Mode

```bash
python demo.py
```

This runs without requiring Google Cloud credentials and demonstrates:
- Intent recognition
- Response generation
- Entity extraction
- Conversation flow

### Test 4: Test Database

```bash
python -c "from modules.database import Database; db = Database(); print('Database initialized with', len(db.get_all_faqs()), 'FAQs')"
```

Expected output: `Database initialized with 5 FAQs`

### Test 5: Test Analytics

```bash
python modules/analytics.py
```

Should display sample analytics statistics.

---

## Using the Application

### Streamlit Web Interface

1. **Start the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Chat Page:**
   - Type a message in the text box and click "Send"
   - Or click the microphone button to record voice
   - View conversation history
   - See intent analysis and confidence scores

3. **Analytics Dashboard:**
   - Click "Analytics" in the sidebar
   - View real-time metrics
   - See intent distribution charts
   - Check error logs

4. **FAQ Manager:**
   - Click "FAQ Manager" in the sidebar
   - View existing FAQs
   - Add new question-answer pairs
   - Track FAQ usage

5. **Settings:**
   - Click "Settings" in the sidebar
   - Check AI configuration status
   - View database location
   - Export analytics data

### CLI Interface

1. **Start the app:**
   ```bash
   python main.py
   ```

2. **Choose session type:**
   - Option 1: Voice session (with microphone)
   - Option 2: Text-only session

3. **Interact:**
   - Follow on-screen prompts
   - Type 'quit' to exit

### REST API

1. **Start the API:**
   ```bash
   python app.py
   ```

2. **Test with curl:**

   **Process text:**
   ```bash
   curl -X POST http://localhost:5000/api/process-text \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, how are you?"}'
   ```

   **Get greeting:**
   ```bash
   curl http://localhost:5000/api/greeting
   ```

   **Health check:**
   ```bash
   curl http://localhost:5000/api/health
   ```

---

## Configuration Options

### Environment Variables

Edit `.env` file to customize:

```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Audio settings
SAMPLE_RATE=16000
AUDIO_CHANNELS=1
CHUNK_SIZE=1024

# Language settings
LANGUAGE_CODE=en-US
VOICE_NAME=en-US-Standard-A

# Optional AI
OPENAI_API_KEY=sk-your-key-here
```

### Bot Configuration

Edit `config/settings.py` to customize:
- Bot name
- Greeting message
- Intent keywords
- Response templates

---

## Troubleshooting

### Issue 1: ImportError for Google Cloud

**Error:**
```
ImportError: cannot import name 'SpeechClient'
```

**Solution:**
```bash
pip install --upgrade google-cloud-speech google-cloud-texttospeech
```

### Issue 2: Credentials Not Found

**Error:**
```
google.auth.exceptions.DefaultCredentialsError
```

**Solution:**
1. Check `.env` file exists
2. Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
3. Ensure JSON key file exists at that path
4. Check file permissions

### Issue 3: PyAudio Installation Fails

**On macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**On Windows:**
Download wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install:
```bash
pip install PyAudio-0.2.11-cp38-cp38-win_amd64.whl
```

### Issue 4: OpenAI API Error

**Error:**
```
openai.error.AuthenticationError
```

**Solution:**
1. Check `OPENAI_API_KEY` in `.env` file
2. Verify key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)
3. Restart the application after updating `.env`

### Issue 5: Streamlit Port Already in Use

**Error:**
```
Address already in use
```

**Solution:**
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Issue 6: Microphone Not Working

**Solutions:**
1. Check system microphone permissions
2. Test microphone with another app
3. For web interface, allow browser microphone access
4. Try text-only mode instead

### Issue 7: Database Errors

**Solution:**
```bash
# Delete existing database and recreate
rm -f data/voice_bot.db
python -c "from modules.database import Database; Database()"
```

### Issue 8: Audio Not Playing

**In Streamlit:**
- Check browser console for errors
- Ensure browser supports HTML5 audio
- Try a different browser (Chrome recommended)

**In CLI:**
- Check speaker volume
- Verify audio file is created in `data/audio/`
- Test with: `afplay data/audio/greeting.mp3` (macOS)

---

## Performance Tips

1. **For faster response times:**
   - Use SSD for database storage
   - Enable OpenAI API for dynamic responses
   - Pre-populate FAQ database

2. **For better accuracy:**
   - Speak clearly into microphone
   - Reduce background noise
   - Use high-quality audio input

3. **For cost optimization:**
   - Use template responses (disable OpenAI)
   - Cache common responses in FAQ
   - Monitor Google Cloud usage

---

## Next Steps

After successful setup:

1. **Add Custom FAQs:**
   - Navigate to FAQ Manager in Streamlit
   - Add domain-specific questions and answers

2. **Customize Responses:**
   - Edit `config/settings.py`
   - Update `RESPONSE_TEMPLATES` dictionary

3. **Monitor Performance:**
   - Check Analytics Dashboard regularly
   - Review error logs
   - Export metrics for analysis

4. **Deploy to Production:**
   - See deployment guides for Streamlit Cloud, Heroku, or Docker
   - Set up proper monitoring
   - Configure backup for database

---

## Getting Help

1. **Check existing documentation:**
   - [README.md](README.md) - Project overview
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
   - [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - Features list

2. **Review logs:**
   - Check terminal output
   - View Analytics Dashboard error logs
   - Query database: `SELECT * FROM error_logs`

3. **Test components individually:**
   - Run demo.py for offline testing
   - Test modules individually (see Testing section)

---

## Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py

# Run CLI
python main.py

# Run API server
python app.py

# Run demo (no credentials needed)
python demo.py

# Test database
python modules/database.py

# Test analytics
python modules/analytics.py

# Deactivate virtual environment
deactivate
```

---

## System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 1GB free disk space
- Internet connection

**Recommended:**
- Python 3.10+
- 8GB RAM
- 5GB free disk space
- Stable internet connection
- SSD storage

---

**You're all set! Run `streamlit run streamlit_app.py` to start using your AI Voice Assistant.**
