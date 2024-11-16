import os
from dotenv import load_dotenv
from pipeline.pipeline_handler import PipelineHandler
from groq import Groq
from voice.microphone_manager import MicrophoneManager
from voice.audio_recorder import AudioRecorder
from voice.whisper import WhisperProcessor

def voice_to_text():
    """
    Handles voice recording and processing to convert speech to text.
    """
    microphone_manager = MicrophoneManager()
    audio_recorder = AudioRecorder(microphone_manager)
    whisper_processor = WhisperProcessor(
        main_path="/Users/mani/Desktop/whisper.cpp/main",
        model_path="/Users/mani/Desktop/whisper.cpp/models/ggml-tiny.en.bin"
    )

    audio_filename = "audio_sample.wav"
    print("Recording audio...")
    audio_recorder.record_audio(audio_filename, duration=7)
    print("Processing audio...")
    processed_text = whisper_processor.process_audio_with_whisper(audio_filename)
    print(processed_text)
    return processed_text

def pipeline_operations(input_text):
    """
    Handles pipeline operations for command generation and execution.
    """
    # Load environment variables
    load_dotenv()

    # Initialize the Groq client
    client = Groq(
        api_key=os.environ["GROQ_API_KEY"]
    )
    
    # Initialize the pipeline handler
    pipeline_handler = PipelineHandler(client)

    # Use the voice-processed text as the request for the pipeline
    print(f"Processing pipeline request: {input_text}")
    result = pipeline_handler.pipeline(input_text)
    return result

def main():
    """
    Unified entry point for voice-to-text and pipeline operations.
    """
    print("Starting voice-to-text conversion...")
    # while(True):
        
    text_output = voice_to_text()  # Get the text output from voice processing
    if "quit" not in text_output:
        if text_output:
            print(f"Voice-to-text output: {text_output}")
            res = pipeline_operations(text_output)
            print(res)  
        else:
            print("Failed to process audio or no text was detected.")

if __name__ == "__main__":
    main()