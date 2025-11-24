"""
Text-to-Speech module using Google Cloud Text-to-Speech API
"""
import os
from google.cloud import texttospeech
from config.settings import Config


class TextToSpeech:
    def __init__(self):
        """Initialize the Text-to-Speech client"""
        # Set credentials
        if Config.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS

        self.client = texttospeech.TextToSpeechClient()

        # Configure voice parameters
        self.voice = texttospeech.VoiceSelectionParams(
            language_code=Config.LANGUAGE_CODE,
            name=Config.VOICE_NAME,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Configure audio output
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )

    def synthesize_speech(self, text, output_file=None):
        """
        Convert text to speech

        Args:
            text (str): Text to convert to speech
            output_file (str, optional): Path to save audio file. If None, returns audio content

        Returns:
            bytes or str: Audio content bytes if output_file is None, else path to saved file
        """
        try:
            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Perform text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )

            # Save or return audio content
            if output_file:
                with open(output_file, 'wb') as out:
                    out.write(response.audio_content)
                return output_file
            else:
                return response.audio_content

        except Exception as e:
            print(f"Error in speech synthesis: {str(e)}")
            return None

    def synthesize_ssml(self, ssml_text, output_file=None):
        """
        Convert SSML formatted text to speech

        Args:
            ssml_text (str): SSML formatted text
            output_file (str, optional): Path to save audio file

        Returns:
            bytes or str: Audio content bytes or file path
        """
        try:
            # Create SSML synthesis input
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

            # Perform text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )

            # Save or return audio content
            if output_file:
                with open(output_file, 'wb') as out:
                    out.write(response.audio_content)
                return output_file
            else:
                return response.audio_content

        except Exception as e:
            print(f"Error in SSML speech synthesis: {str(e)}")
            return None

    def change_voice(self, language_code=None, voice_name=None, gender=None):
        """
        Change voice parameters

        Args:
            language_code (str, optional): Language code (e.g., 'en-US')
            voice_name (str, optional): Specific voice name
            gender (str, optional): Voice gender ('MALE', 'FEMALE', 'NEUTRAL')
        """
        if language_code:
            self.voice.language_code = language_code

        if voice_name:
            self.voice.name = voice_name

        if gender:
            gender_map = {
                'MALE': texttospeech.SsmlVoiceGender.MALE,
                'FEMALE': texttospeech.SsmlVoiceGender.FEMALE,
                'NEUTRAL': texttospeech.SsmlVoiceGender.NEUTRAL
            }
            self.voice.ssml_gender = gender_map.get(gender.upper(), texttospeech.SsmlVoiceGender.NEUTRAL)

    def adjust_audio_settings(self, speaking_rate=None, pitch=None):
        """
        Adjust audio output settings

        Args:
            speaking_rate (float, optional): Speaking rate (0.25 to 4.0, default 1.0)
            pitch (float, optional): Audio pitch (-20.0 to 20.0, default 0.0)
        """
        if speaking_rate is not None:
            self.audio_config.speaking_rate = speaking_rate

        if pitch is not None:
            self.audio_config.pitch = pitch


if __name__ == "__main__":
    # Simple test
    print("Text-to-Speech module initialized successfully")
    tts = TextToSpeech()
    print("Client created successfully")
