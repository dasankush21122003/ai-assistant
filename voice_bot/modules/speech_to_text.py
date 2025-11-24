"""
Speech-to-Text module using Google Cloud Speech-to-Text API
"""
import io
import os
from google.cloud import speech
from google.cloud.speech import RecognitionConfig, RecognitionAudio
from config.settings import Config


class SpeechToText:
    def __init__(self):
        """Initialize the Speech-to-Text client"""
        # Set credentials
        if Config.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS

        self.client = speech.SpeechClient()
        self.config = RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=Config.SAMPLE_RATE,
            language_code=Config.LANGUAGE_CODE,
            enable_automatic_punctuation=True,
        )

    def transcribe_audio_file(self, audio_file_path):
        """
        Transcribe audio from a file

        Args:
            audio_file_path (str): Path to the audio file

        Returns:
            str: Transcribed text
        """
        try:
            with io.open(audio_file_path, 'rb') as audio_file:
                content = audio_file.read()

            audio = RecognitionAudio(content=content)
            response = self.client.recognize(config=self.config, audio=audio)

            # Combine all transcripts
            transcripts = []
            for result in response.results:
                transcripts.append(result.alternatives[0].transcript)

            return ' '.join(transcripts)

        except Exception as e:
            print(f"Error in transcription: {str(e)}")
            return None

    def transcribe_audio_stream(self, audio_content):
        """
        Transcribe audio from raw audio content (bytes)

        Args:
            audio_content (bytes): Raw audio data

        Returns:
            str: Transcribed text
        """
        try:
            audio = RecognitionAudio(content=audio_content)
            response = self.client.recognize(config=self.config, audio=audio)

            # Combine all transcripts
            transcripts = []
            for result in response.results:
                transcripts.append(result.alternatives[0].transcript)

            return ' '.join(transcripts)

        except Exception as e:
            print(f"Error in transcription: {str(e)}")
            return None

    def transcribe_streaming(self, audio_generator):
        """
        Transcribe audio stream in real-time

        Args:
            audio_generator: Generator yielding audio chunks

        Yields:
            str: Transcribed text chunks
        """
        try:
            streaming_config = speech.StreamingRecognitionConfig(
                config=self.config,
                interim_results=True
            )

            requests = (
                speech.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in audio_generator
            )

            responses = self.client.streaming_recognize(
                config=streaming_config,
                requests=requests
            )

            for response in responses:
                for result in response.results:
                    if result.is_final:
                        yield result.alternatives[0].transcript

        except Exception as e:
            print(f"Error in streaming transcription: {str(e)}")
            yield None


if __name__ == "__main__":
    # Simple test
    print("Speech-to-Text module initialized successfully")
    stt = SpeechToText()
    print("Client created successfully")
