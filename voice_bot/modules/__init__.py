"""
Voice Bot Modules Package
"""

__version__ = "1.0.0"
__author__ = "AI Intern Project"

from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .intent_recognizer import IntentRecognizer
from .response_generator import ResponseGenerator
from .audio_recorder import AudioRecorder, AudioPlayer

__all__ = [
    'SpeechToText',
    'TextToSpeech',
    'IntentRecognizer',
    'ResponseGenerator',
    'AudioRecorder',
    'AudioPlayer'
]
