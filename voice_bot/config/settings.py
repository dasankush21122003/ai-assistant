"""
Configuration settings for the Voice Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Cloud Configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID')

    # Audio Configuration
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', 16000))
    AUDIO_CHANNELS = int(os.getenv('AUDIO_CHANNELS', 1))
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1024))

    # Speech Recognition Configuration
    LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-US')

    # Text-to-Speech Configuration
    VOICE_NAME = os.getenv('VOICE_NAME', 'en-US-Standard-A')

    # Bot Configuration
    BOT_NAME = "CustomerBot"
    GREETING_MESSAGE = "Hello! I am your customer service assistant. How can I help you today?"

    # Supported intents and their keywords
    INTENT_KEYWORDS = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
        'product_info': ['product', 'item', 'price', 'cost', 'available', 'stock'],
        'order_status': ['order', 'delivery', 'shipping', 'track', 'status'],
        'account': ['account', 'profile', 'login', 'password', 'reset'],
        'support': ['help', 'support', 'issue', 'problem', 'complaint'],
        'farewell': ['bye', 'goodbye', 'thanks', 'thank you', 'exit', 'quit']
    }

    # Response templates for each intent
    RESPONSE_TEMPLATES = {
        'greeting': [
            "Hello! How can I assist you today?",
            "Hi there! What can I do for you?",
            "Welcome! I'm here to help you."
        ],
        'product_info': [
            "I can help you with product information. Which product are you interested in?",
            "Sure! Let me get you the product details. Can you specify the product name?"
        ],
        'order_status': [
            "I can check your order status. Could you provide your order number?",
            "Let me help you track your order. What's your order ID?"
        ],
        'account': [
            "I can assist with account-related queries. What do you need help with?",
            "I'm here to help with your account. Please describe your issue."
        ],
        'support': [
            "I'm sorry you're experiencing an issue. Can you describe the problem in detail?",
            "I'm here to help resolve your issue. What seems to be the problem?"
        ],
        'farewell': [
            "Thank you for contacting us! Have a great day!",
            "Goodbye! Feel free to reach out if you need anything else.",
            "It was nice helping you. Take care!"
        ],
        'unknown': [
            "I'm not sure I understand. Could you please rephrase that?",
            "I didn't quite catch that. Can you provide more details?",
            "I'm still learning. Could you ask that in a different way?"
        ]
    }

    @classmethod
    def validate(cls):
        """Validate that required environment variables are set"""
        if not cls.GOOGLE_APPLICATION_CREDENTIALS:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in environment")
        if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            raise ValueError(f"Google credentials file not found at: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
        return True
