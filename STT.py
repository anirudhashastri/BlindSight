import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import os
import re

class STT:
    def __init__(self):
        self.microphone = self.list_and_select_microphone()

    def list_and_select_microphone(self):
        """
        Lists all available microphones and allows the user to select one.

        Returns:
            dict: Information about the selected microphone.
        """
        try:
            # Fetch all audio devices
            devices = sd.query_devices()
            # Filter out devices that have input channels (microphones)
            input_devices = [device for device in devices if device['max_input_channels'] > 0]
            if not input_devices:
                print("No input devices (microphones) found.")
                return None

            # Display the list of available microphones
            print("\nAvailable Microphones:")
            for idx, device in enumerate(input_devices):
                print(f"{idx}: {device['name']} "
                      f"(Channels: {device['max_input_channels']}, "
                      f"Default Sample Rate: {device['default_samplerate']})")

            # Prompt the user to select a microphone

            try:
                selection = int(input("\nSelect a microphone by index: "))
                if 0 <= selection < len(input_devices):
                    selected_device = input_devices[selection]
                    print(f"\nSelected Microphone: {selected_device['name']}")
                    return selected_device
                else:
                    print(f"Please enter a number between 0 and {len(input_devices) - 1}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def record_audio(self, filename, duration=5):
        """
        Records audio from the selected microphone and saves it as a .wav file at 16 kHz.

        Parameters:
            filename (str): The name of the .wav file to save the recording.
            duration (int): The duration of the recording in seconds.
        """
        if not self.microphone:
            print("No microphone selected. Exiting.")
            return

        # Set the selected microphone as the input device
        sd.default.device = self.microphone['name']

        # Define 16 kHz as the sample rate
        sample_rate = 16000
        print("Recording...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()  # Wait until the recording is finished
        print("Recording complete.")

        # Save as a .wav file at 16-bit PCM format
        audio_data = np.int16(audio_data * 32767)
        write(filename, sample_rate, audio_data)
        print(f"Audio saved as {filename}")

    def process_audio_with_whisper(self, file_path):
        """
        Processes a WAV file using the Whisper.cpp binary, extracts plain text sentences from the output,
        and deletes the file after processing.

        Parameters:
            file_path (str): The full path to the WAV file to be processed.
        """
        # Define the path to the main binary and the model
        main_path = os.environ['WHISPER_MAIN_PATH']
        model_path = os.environ['WHISPER_MODEL_PATH']

        # Check if the WAV file exists
        if not os.path.isfile(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            return

        # Construct the command
        command = [
            main_path,
            "-m", model_path,
            "-f", file_path
        ]

        try:
            # Execute the command
            print(f"Running command: {' '.join(command)}")
            result = subprocess.run(command, check=True, text=True, capture_output=True)

            # Extract output and clean it
            raw_output = result.stdout
            # Use regex to remove timestamps and keep only the sentences
            sentences = re.findall(r"(?<=\]\s).*", raw_output)
            plain_text = " ".join(sentences).strip()

            # Further split sentences using punctuation and join with proper spacing
            cleaned_text = re.sub(r"([.?!])", r"\1\n", plain_text).strip()

            # Print the cleaned text
            print("Processed Text:")
            print(cleaned_text)
            return cleaned_text
        

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while processing the file: {e}")
            print(f"Error Output: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            # Delete the file after processing
            try:
                os.remove(file_path)
                print(f"File '{file_path}' has been deleted.")
            except Exception as e:
                print(f"An error occurred while deleting the file: {e}")


if __name__ == "__main__":
    soundbox = STT()
    soundbox.record_audio("audio_sample.wav", duration=7)
    soundbox.process_audio_with_whisper("audio_sample.wav")