import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import os
import re
from pynput import keyboard
import threading
import pyttsx3
import time
import queue


class AudioRecorder:
    def __init__(self):
        self.microphone = self.list_and_select_microphone()
        self.is_recording = False
        self.stream = None
        self.audio_chunks = []
        self.sample_rate = 16000

    def list_and_select_microphone(self):
        try:
            devices = sd.query_devices()
            input_devices = [device for device in devices if device['max_input_channels'] > 0]
            if not input_devices:
                print("No input devices found.")
                return None

            print("\nAvailable Microphones:")
            for idx, device in enumerate(input_devices):
                print(f"{idx}: {device['name']} "
                      f"(Channels: {device['max_input_channels']}, "
                      f"Default Sample Rate: {device['default_samplerate']})")

            selection = int(input("\nSelect a microphone by index: "))
            if 0 <= selection < len(input_devices):
                selected_device = input_devices[selection]
                print(f"\nSelected Microphone: {selected_device['name']}")
                return selected_device
            else:
                print(f"Invalid selection.")
                return None

        except Exception as e:
            print(f"Error: {e}")
            return None

    def start_recording(self):
        if not self.microphone:
            print("No microphone selected.")
            return

        self.audio_chunks = []
        self.is_recording = True

        def callback(indata, frames, time, status):
            if status:
                print(status)
            if self.is_recording:
                self.audio_chunks.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=callback,
                device=self.microphone['name']
            )
            self.stream.start()
            print("Recording started...")

        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False

    def stop_recording(self):
        if not self.is_recording or not self.audio_chunks:
            print("No recording to stop.")
            return None

        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        audio_data = np.concatenate(self.audio_chunks, axis=0)
        audio_data = np.int16(audio_data * 32767)
        filename = f"audio_sample_{time.time()}.wav"
        write(filename, self.sample_rate, audio_data)
        print(f"Recording stopped. Audio saved as {filename}")
        return filename


class Transcriber:
    def __init__(self):
        self.main_path = "whisper.cpp/main"
        self.model_path = "whisper.cpp/models/ggml-tiny.en.bin"

    def transcribe(self, file_path):
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return None

        try:
            command = [self.main_path, "-m", self.model_path, "-f", file_path]
            print("Processing audio...")
            result = subprocess.run(command, check=True, text=True, capture_output=True)

            sentences = re.findall(r"(?<=\]\s).*", result.stdout)
            text = " ".join(sentences).strip()

            print("Transcribed Text:")
            print(text)
            return text

        except Exception as e:
            print(f"Transcription error: {e}")
            return None
        finally:
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except:
                pass


class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.is_speaking = False
        self.stop_speech = False  # Flag to stop speech immediately

    def initialize_engine(self):
        """Reinitialize the pyttsx3 engine if needed to avoid 'run loop already started' error."""
        if hasattr(self.engine, '_inLoop') and self.engine._inLoop:
            self.engine.endLoop()  # Stop the existing loop if it's running
            self.engine = pyttsx3.init()  # Reinitialize the engine to avoid loop issues

    def speak(self, text):
        """Override the speak method to handle interruption."""
        if not text:
            return

        self.stop_speech = False
        self.is_speaking = True

        try:
            self.initialize_engine()  # Ensure we are not in an existing loop
            
            # Check for the stop flag before starting speech
            if self.stop_speech:
                print("Speech interrupted.")
                self.engine.stop()  # Stop the current speech immediately
                self.is_speaking = False
                return
            
            self.engine.say(text)
            self.engine.runAndWait()

        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self.is_speaking = False

    def stop(self):
        if self.engine and self.is_speaking:
            self.engine.stop()
            self.is_speaking = False


class VoiceSystem:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.speaker = Speaker()
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.running = True

        # Start worker threads
        self.transcription_thread = threading.Thread(target=self.transcription_worker, daemon=True)
        self.speech_thread = threading.Thread(target=self.speech_worker, daemon=True)
        self.transcription_thread.start()
        self.speech_thread.start()

    def transcription_worker(self):
        while self.running:
            try:
                audio_file = self.audio_queue.get(timeout=1)
                if audio_file:
                    text = self.transcriber.transcribe(audio_file)
                    if text:
                        self.text_queue.put(text)
                self.audio_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Transcription error: {e}")

    def speech_worker(self):
        while self.running:
            try:
                text = self.text_queue.get(timeout=1)
                if text:
                    self.speaker.speak(text)
                self.text_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Speech error: {e}")

    def on_press(self, key):
        if key == keyboard.Key.space:
            # Interrupt the speaker immediately when space is pressed again
            if self.speaker.is_speaking:
                print("Interrupting speech...")
                self.speaker.stop()

            if not self.recorder.is_recording:
                self.recorder.start_recording()

    def on_release(self, key):
        if key == keyboard.Key.space and self.recorder.is_recording:
            audio_file = self.recorder.stop_recording()
            if audio_file:
                self.audio_queue.put(audio_file)

    def cleanup(self):
        self.running = False
        self.recorder.is_recording = False
        self.speaker.stop()

    def run(self):
        print("Hold spacebar to record. Press 'q' to quit.")
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    voice_system = VoiceSystem()
    voice_system.run()