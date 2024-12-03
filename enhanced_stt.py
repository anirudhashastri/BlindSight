import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import os
import re
import sys
import threading
import queue
import time
from pynput import keyboard
from datetime import datetime
from log_config import setup_logger
from dotenv import load_dotenv

class EnhancedSTT:
    def __init__(self):
        # Audio configuration
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = np.int16
        
        # Recording state
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        self.buffer_timeout = 0.5  # Buffer timeout in seconds
        
        # Feedback sounds
        self.start_beep_freq = 880  # Hz
        self.stop_beep_freq = 440   # Hz
        self.beep_duration = 0.1    # seconds
        
        # Setup logging
        self._setup_logging()
        
        # Initialize microphone
        self.microphone = self.list_and_select_microphone()
        
        # Load environment variables
        load_dotenv()
        
    def _setup_logging(self):
        """Setup logging for the STT system."""

        self.logger = setup_logger('STT')
        self.logger.info("Enhanced STT system initialized")

    def _play_beep(self, frequency, duration):
        """Play a beep sound for user feedback."""
        try:
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            beep = 0.3 * np.sin(2 * np.pi * frequency * t)
            sd.play(beep, self.sample_rate)
            sd.wait()
        except Exception as e:
            self.logger.error(f"Error playing feedback sound: {e}")

    def _record_callback(self, indata, frames, time, status):
        """Callback function for audio recording."""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def _start_recording(self):
        """Start the audio recording process."""
        self.logger.info("Recording started")
        self.is_recording = True
        self._play_beep(self.start_beep_freq, self.beep_duration)
        print("\nRecording... (Hold spacebar)")
        
        # Clear any existing audio in the queue
        while not self.audio_queue.empty():
            self.audio_queue.get()

        try:
            with sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._record_callback,
                device=self.microphone['index'] if self.microphone else None
            ):
                while self.is_recording:
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Error during recording: {e}")
            self.is_recording = False

    def _stop_recording(self):
        """Stop the audio recording process."""
        self.is_recording = False
        self._play_beep(self.stop_beep_freq, self.beep_duration)
        self.logger.info("Recording stopped")
        print("\nProcessing audio...")

    def record_press_hold(self, output_file="audio_sample.wav"):
        """
        Record audio using press-and-hold spacebar functionality.
        
        Args:
            output_file (str): Path to save the recorded audio
        
        Returns:
            bool: True if recording was successful, False otherwise
        """
        audio_data = []
        
        def on_press(key):
            if key == keyboard.Key.space and not self.is_recording:
                self.recording_thread = threading.Thread(target=self._start_recording)
                self.recording_thread.start()

        def on_release(key):
            if key == keyboard.Key.space and self.is_recording:
                self._stop_recording()
                return False  # Stop listener

        # Start keyboard listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

        # Add buffer timeout to catch trailing speech
        time.sleep(self.buffer_timeout)

        # Collect all audio data from queue
        try:
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())

            if not audio_data:
                self.logger.warning("No audio data recorded")
                return False

            # Concatenate and save audio data
            audio_array = np.concatenate(audio_data, axis=0)
            audio_array = np.int16(audio_array * 32767)
            write(output_file, self.sample_rate, audio_array)
            self.logger.info(f"Audio saved to {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving audio: {e}")
            return False

    def process_audio_with_whisper(self, file_path):
        """Process recorded audio with Whisper."""
        try:
            # Get Whisper paths from environment
            main_path = os.environ['WHISPER_MAIN_PATH']
            model_path = os.environ['WHISPER_MODEL_PATH']

            if not all([main_path, model_path]):
                self.logger.error("Whisper paths not properly configured")
                return None

            # Verify files exist
            if not all(os.path.isfile(p) for p in [main_path, model_path, file_path]):
                self.logger.error("Required files missing")
                return None

            # Process with Whisper
            command = [main_path, "-m", model_path, "-f", file_path]
            self.logger.info(f"Running Whisper command: {' '.join(command)}")
            
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            
            # Clean and process output
            sentences = re.findall(r"(?<=\]\s).*", result.stdout)
            text = " ".join(sentences).strip()
            
            if not text:
                self.logger.warning("No text extracted from audio")
                return None

            cleaned_text = re.sub(r"([.?!])", r"\1\n", text).strip()
            self.logger.info(f"Processed text: {cleaned_text}")
            
            return cleaned_text

        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
            return None

        finally:
            # Cleanup
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                self.logger.error(f"Error cleaning up file: {e}")

    def list_and_select_microphone(self):
        """List and select available microphones."""
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if not input_devices:
                self.logger.error("No input devices found")
                return None

            self.logger.info("\nAvailable Microphones:")
            print("\nAvailable Microphones:")
            for idx, device in enumerate(input_devices):
                print(f"{idx}: {device['name']}")
                self.logger.info(f"{idx}: {device['name']}")

            while True:
                try:
                    selection = input("\nSelect microphone index (or 'exit'): ")
                    if selection.lower() == 'exit':
                        return None
                    
                    selection = int(selection)
                    if 0 <= selection < len(input_devices):
                        selected_device = input_devices[selection]
                        self.logger.info(f"Selected: {selected_device['name']}")
                        return selected_device
                    
                    print(f"Please enter 0-{len(input_devices)-1}")
                    
                except ValueError:
                    print("Please enter a valid number")

        except Exception as e:
            self.logger.error(f"Error listing microphones: {e}")
            return None