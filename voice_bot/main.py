"""
Main Voice Bot - Orchestrates all modules for voice-based customer interaction
"""
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.intent_recognizer import IntentRecognizer
from modules.response_generator import ResponseGenerator
from modules.audio_recorder import AudioRecorder, AudioPlayer
from config.settings import Config


class VoiceBot:
    """Main Voice Bot class that orchestrates all components"""

    def __init__(self):
        """Initialize the Voice Bot with all necessary components"""
        print("Initializing Voice Bot...")

        try:
            # Validate configuration
            Config.validate()

            # Initialize all modules
            self.stt = SpeechToText()
            self.tts = TextToSpeech()
            self.intent_recognizer = IntentRecognizer()
            self.response_generator = ResponseGenerator()
            self.audio_recorder = AudioRecorder()
            self.audio_player = AudioPlayer()

            self.is_running = False
            self.conversation_active = False

            # Create output directory for audio files
            self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'audio')
            os.makedirs(self.output_dir, exist_ok=True)

            print(f"✓ Voice Bot initialized successfully as '{Config.BOT_NAME}'")

        except Exception as e:
            print(f"✗ Error initializing Voice Bot: {str(e)}")
            raise

    def greet_user(self):
        """Greet the user when starting conversation"""
        greeting = Config.GREETING_MESSAGE
        print(f"\n{Config.BOT_NAME}: {greeting}")

        # Convert greeting to speech
        audio_file = os.path.join(self.output_dir, 'greeting.mp3')
        self.tts.synthesize_speech(greeting, audio_file)
        self.audio_player.play_audio_file(audio_file)

    def process_voice_input(self, audio_file_path):
        """
        Process voice input through the complete pipeline

        Args:
            audio_file_path (str): Path to the audio file

        Returns:
            Dict: Processing results
        """
        print("\n--- Processing Voice Input ---")

        # Step 1: Speech to Text
        print("1. Transcribing speech...")
        user_text = self.stt.transcribe_audio_file(audio_file_path)

        if not user_text:
            print("✗ Failed to transcribe audio")
            return None

        print(f"   User said: '{user_text}'")

        # Step 2: Intent Recognition
        print("2. Recognizing intent...")
        analysis = self.intent_recognizer.analyze_query(user_text)
        intent = analysis['intent']
        confidence = analysis['confidence']
        entities = analysis['entities']

        print(f"   Intent: {intent} (confidence: {confidence:.2f})")
        if entities:
            print(f"   Entities: {entities}")

        # Step 3: Generate Response
        print("3. Generating response...")
        response_text = self.response_generator.generate_response(
            intent,
            entities,
            analysis['context']
        )

        print(f"   Bot response: '{response_text}'")

        # Step 4: Text to Speech
        print("4. Converting response to speech...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response_audio_file = os.path.join(self.output_dir, f'response_{timestamp}.mp3')
        self.tts.synthesize_speech(response_text, response_audio_file)

        print("✓ Processing complete\n")

        return {
            'user_text': user_text,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'response_text': response_text,
            'response_audio': response_audio_file
        }

    def interactive_session(self):
        """Run an interactive voice bot session"""
        print("\n" + "=" * 60)
        print("Voice Bot Interactive Session")
        print("=" * 60)

        self.conversation_active = True
        self.greet_user()

        turn_count = 0

        while self.conversation_active:
            turn_count += 1
            print(f"\n--- Turn {turn_count} ---")
            print("Press Enter to start recording (or type 'quit' to exit): ", end='')

            user_input = input()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Exiting conversation...")
                self.say_goodbye()
                break

            # Record audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_audio_file = os.path.join(self.output_dir, f'input_{timestamp}.wav')

            print("\n🎤 Recording... (Speak now, will stop after 5 seconds of recording)")
            self.audio_recorder.record_fixed_duration(5, input_audio_file)

            # Process the voice input
            result = self.process_voice_input(input_audio_file)

            if result:
                # Play the response
                print(f"\n🔊 {Config.BOT_NAME}: {result['response_text']}")
                self.audio_player.play_audio_file(result['response_audio'])

                # Check if user wants to end conversation
                if result['intent'] == 'farewell':
                    print("\nEnding conversation as requested.")
                    self.conversation_active = False
            else:
                print("Failed to process voice input. Please try again.")

        print("\n" + "=" * 60)
        print("Session ended. Thank you!")
        print("=" * 60)

    def say_goodbye(self):
        """Say goodbye to the user"""
        farewell = "Thank you for using our service. Goodbye!"
        print(f"\n{Config.BOT_NAME}: {farewell}")

        audio_file = os.path.join(self.output_dir, 'goodbye.mp3')
        self.tts.synthesize_speech(farewell, audio_file)
        self.audio_player.play_audio_file(audio_file)

    def process_text_input(self, text):
        """
        Process text input (useful for testing without voice)

        Args:
            text (str): User input text

        Returns:
            str: Bot response
        """
        # Intent Recognition
        analysis = self.intent_recognizer.analyze_query(text)

        # Generate Response
        response_text = self.response_generator.generate_response(
            analysis['intent'],
            analysis['entities'],
            analysis['context']
        )

        return response_text

    def text_only_session(self):
        """Run a text-only session (no voice I/O) for testing"""
        print("\n" + "=" * 60)
        print("Voice Bot Text-Only Session (Testing Mode)")
        print("=" * 60)
        print("Type 'quit' to exit\n")

        self.conversation_active = True
        print(f"{Config.BOT_NAME}: {Config.GREETING_MESSAGE}\n")

        while self.conversation_active:
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Config.BOT_NAME}: Thank you for chatting. Goodbye!")
                break

            # Process text input
            response = self.process_text_input(user_input)
            print(f"{Config.BOT_NAME}: {response}\n")

            # Check for farewell intent
            analysis = self.intent_recognizer.analyze_query(user_input)
            if analysis['intent'] == 'farewell':
                self.conversation_active = False

        print("\n" + "=" * 60)
        print("Session ended.")
        print("=" * 60)

    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up resources...")
        self.audio_recorder.cleanup()
        self.audio_player.cleanup()
        print("Cleanup complete.")


def main():
    """Main entry point for the Voice Bot"""
    try:
        # Create and initialize the bot
        bot = VoiceBot()

        # Ask user for session type
        print("\nChoose session type:")
        print("1. Interactive Voice Session (requires microphone and speakers)")
        print("2. Text-Only Session (for testing)")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ")

        if choice == '1':
            bot.interactive_session()
        elif choice == '2':
            bot.text_only_session()
        elif choice == '3':
            print("Exiting...")
        else:
            print("Invalid choice. Exiting...")

        # Cleanup
        bot.cleanup()

    except KeyboardInterrupt:
        print("\n\nSession interrupted by user.")
        if 'bot' in locals():
            bot.cleanup()

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
