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

    def record(self):
        if not self.microphone:
            print("No microphone selected.")
            return None

        filename = f"audio_sample_{time.time()}.wav"
        sample_rate = 16000
        audio_chunks = []
        
        if self.stream is not None:
            self.stream.close()
            self.stream = None

        def callback(indata, frames, time, status):
            if status:
                print(status)
            if self.is_recording:
                audio_chunks.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                callback=callback,
                device=self.microphone['name']
            )
            
            with self.stream:
                print("Recording... Hold spacebar to continue.")
                while self.is_recording:
                    time.sleep(0.1)

            if audio_chunks:
                audio_data = np.concatenate(audio_chunks, axis=0)
                audio_data = np.int16(audio_data * 32767)
                write(filename, sample_rate, audio_data)
                print(f"Audio saved as {filename}")
                return filename
            
            return None

        except Exception as e:
            print(f"Recording error: {e}")
            return None
        finally:
            if self.stream is not None:
                self.stream.close()
                self.stream = None


class Transcriber:
    def __init__(self):
        self.main_path = "whisper_cpp/main"
        self.model_path = "whisper_cpp/models/ggml-tiny.en.bin"

    def transcribe(self, file_path):
        """Transcribes audio file to text."""
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
            except Exception as e:
                print(f"Error deleting file: {e}")
                
                pass

class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Remove threading-related attributes
        # self.speaking_thread = None
        # self.stop_speaking = False

    def speak(self, text):
        """Speaks the provided text."""
        if not text:
            return
        try:
            print('speaking...')

            self.engine.startLoop(False)
            print('loop started')
            
            self.engine.say(text)
            
            print('finished speaking')
            self.engine.endLoop()
            print('loop ended')
            
            # self.engine.runAndWait()
        except Exception as e:
            print(f"Error in speak: {e}")

    def stop(self):
        """Stops current speech."""
        self.engine.stop()



class VoiceSystem:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.speaker = Speaker()
        self.processing = False
        self.processing_thread = None

    def record_and_transcribe(self):
        """Records audio and returns transcribed text."""
        try:
            audio_file = self.recorder.record()
            if audio_file:
                text = self.transcriber.transcribe(audio_file)
                return text
        except Exception as e:
            print(f"Error in record_and_transcribe: {e}")
        finally:
            self.processing = False
        return None

    def on_press(self, key):
        try:
            if key == keyboard.Key.space and not self.recorder.is_recording:
                if self.processing_thread and self.processing_thread.is_alive():

                    print("Still processing previous recording...")
                    return

                self.speaker.stop()  # Stop any ongoing speech
                print("Recording started...")
                self.recorder.is_recording = True
                self.processing = True

                def process_audio():
                    try:
                        text = self.record_and_transcribe()
                        if text:
                            self.speaker.speak(text)
                            # self.speaker.speak('OK DONE SPEAKING')
                    finally:
                        self.processing = False
                        self.processing_thread = None
                        print("\nReady for next recording. Hold spacebar to record.")

                self.processing_thread = threading.Thread(target=process_audio, daemon=True)

                self.processing_thread.start()


            elif key.char == 'q':
                self.recorder.is_recording = False
                self.speaker.stop()
                if self.recorder.stream:
                    self.recorder.stream.close()
                print("\nExiting...")
                os._exit(0)
        except AttributeError:
            pass

    def on_release(self, key):
        if key == keyboard.Key.space and self.recorder.is_recording:
            print("Recording stopped...")
            self.recorder.is_recording = False

    def run(self):
        """Runs the voice system with spacebar control."""
        print("Hold spacebar to record. Press 'q' to quit.")

        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            listener.join()

            
# Example usage:
if __name__ == "__main__":
    # Run the complete system with spacebar control
    voice_system = VoiceSystem()
    voice_system.run()

#     # Or use components individually:
#     # """
#     # Initialize components
#     recorder = AudioRecorder()
#     transcriber = Transcriber()
#     speaker = Speaker()

#     # Record and transcribe
#     while True:
#         recorder.is_recording = True
#         audio_file = recorder.record()
#         recorder.
#         text = transcriber.transcribe(audio_file)

#         if text:
#             speaker.speak(text)
        
#         # recorder.is_recording = False

#     # Speak text
#     speaker.speak("Hello, this is a test")
#     # time.sleep(2)  # Wait for speech to complete
#     speaker.stop()  # Stop speaking
#     # """
