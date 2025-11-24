"""
Audio Recording utility for capturing voice input
"""
import wave
import pyaudio
import os
from config.settings import Config


class AudioRecorder:
    def __init__(self):
        """Initialize the audio recorder"""
        self.sample_rate = Config.SAMPLE_RATE
        self.channels = Config.AUDIO_CHANNELS
        self.chunk_size = Config.CHUNK_SIZE
        self.audio_format = pyaudio.paInt16

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []

    def start_recording(self):
        """Start recording audio"""
        self.frames = []
        self.stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        print("Recording started... (Press Ctrl+C or call stop_recording() to stop)")

    def record_chunk(self):
        """Record a single chunk of audio"""
        if self.stream:
            data = self.stream.read(self.chunk_size)
            self.frames.append(data)
            return data
        return None

    def stop_recording(self):
        """Stop recording audio"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        print("Recording stopped.")

    def save_recording(self, filename):
        """
        Save the recorded audio to a WAV file

        Args:
            filename (str): Path to save the audio file

        Returns:
            str: Path to the saved file
        """
        if not self.frames:
            print("No audio data to save.")
            return None

        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        # Save as WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))

        print(f"Audio saved to: {filename}")
        return filename

    def record_fixed_duration(self, duration_seconds, output_file):
        """
        Record audio for a fixed duration

        Args:
            duration_seconds (int): Duration to record in seconds
            output_file (str): Path to save the recording

        Returns:
            str: Path to the saved file
        """
        print(f"Recording for {duration_seconds} seconds...")

        self.start_recording()

        # Calculate number of chunks to record
        chunks_to_record = int(self.sample_rate / self.chunk_size * duration_seconds)

        for i in range(chunks_to_record):
            self.record_chunk()

        self.stop_recording()

        return self.save_recording(output_file)

    def record_until_silence(self, silence_threshold=500, silence_duration=2.0, output_file=None):
        """
        Record audio until silence is detected

        Args:
            silence_threshold (int): Amplitude threshold for silence detection
            silence_duration (float): Duration of silence to trigger stop (seconds)
            output_file (str, optional): Path to save the recording

        Returns:
            str or bytes: Path to saved file or audio bytes
        """
        import numpy as np

        print("Recording... (speak now, will stop after silence)")

        self.start_recording()

        silence_chunks = int(silence_duration * self.sample_rate / self.chunk_size)
        silent_chunk_count = 0

        try:
            while True:
                data = self.record_chunk()

                # Convert bytes to numpy array for amplitude analysis
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitude = np.abs(audio_data).mean()

                if amplitude < silence_threshold:
                    silent_chunk_count += 1
                    if silent_chunk_count >= silence_chunks:
                        print("Silence detected, stopping recording.")
                        break
                else:
                    silent_chunk_count = 0

        except KeyboardInterrupt:
            print("\nRecording interrupted by user.")

        self.stop_recording()

        if output_file:
            return self.save_recording(output_file)
        else:
            return b''.join(self.frames)

    def get_audio_bytes(self):
        """
        Get recorded audio as bytes

        Returns:
            bytes: Audio data
        """
        return b''.join(self.frames)

    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()


class AudioPlayer:
    """Simple audio player for playing back audio files"""

    def __init__(self):
        """Initialize the audio player"""
        self.audio = pyaudio.PyAudio()

    def play_audio_file(self, filename):
        """
        Play an audio file

        Args:
            filename (str): Path to the audio file
        """
        try:
            with wave.open(filename, 'rb') as wf:
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )

                print(f"Playing: {filename}")

                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)

                stream.stop_stream()
                stream.close()

                print("Playback finished.")

        except Exception as e:
            print(f"Error playing audio: {str(e)}")

    def play_audio_bytes(self, audio_bytes, sample_rate=16000, channels=1):
        """
        Play audio from bytes

        Args:
            audio_bytes (bytes): Audio data
            sample_rate (int): Sample rate
            channels (int): Number of channels
        """
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                output=True
            )

            stream.write(audio_bytes)
            stream.stop_stream()
            stream.close()

        except Exception as e:
            print(f"Error playing audio: {str(e)}")

    def cleanup(self):
        """Clean up resources"""
        self.audio.terminate()


if __name__ == "__main__":
    # Simple test
    recorder = AudioRecorder()
    print("Audio Recorder module initialized successfully")

    # Test recording for 3 seconds
    # output_file = "test_recording.wav"
    # recorder.record_fixed_duration(3, output_file)

    # Test playback
    # player = AudioPlayer()
    # player.play_audio_file(output_file)

    recorder.cleanup()
    # player.cleanup()
