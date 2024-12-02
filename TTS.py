from yapper import Yapper, PiperSpeaker, PiperVoice, PiperQuality
import logging
import sys
import os
from datetime import datetime
from pynput import keyboard
import threading

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Generate timestamp for log filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/blindsight_{timestamp}.log")
    ]
)

# Create logger for the specific module
logger = logging.getLogger(__name__)
logger.info(f"Logging initialized for {__name__}")

# Initialize Yapper with PiperSpeaker for better quality
try:
    speaker = PiperSpeaker(
        voice=PiperVoice.AMY,  # Using AMY voice as default
        quality=PiperQuality.MEDIUM  # Medium quality for balance of speed and quality
    )
    yapper = Yapper(speaker=speaker, plain=True)  # Using plain mode to avoid LLM processing
    logger.info("Yapper TTS initialized successfully with PiperSpeaker")
except Exception as e:
    logger.error(f"Failed to initialize Yapper with PiperSpeaker: {e}")
    # Fallback to default speaker
    yapper = Yapper(plain=True)
    logger.info("Falling back to default Yapper speaker")

# Global flag for speech interruption
speaking = False

def on_press(key):
    """
    Callback function for keyboard listener.
    Sets the global 'speaking' flag to False to interrupt speech.
    
    Args:
        key: The key that was pressed.
    
    Returns:
        False to stop the listener.
    """
    global speaking
    logger.info("Interrupt signal received. Stopping speech.")
    speaking = False
    return False

def speak(text):
    """
    Speaks the provided text using Yapper TTS with support for interruption.
    
    Args:
        text (str): The text to be spoken.
    """
    global speaking
    speaking = True
    
    # Create a thread for the keyboard listener
    def keyboard_listener():
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    
    # Create and start the keyboard listener thread
    listener_thread = threading.Thread(target=keyboard_listener)
    listener_thread.daemon = True
    listener_thread.start()
    logger.debug("Keyboard listener thread started.")
    
    # Split text into sentences or chunks for more responsive interruption
    chunks = text.split('.')
    
    for chunk in chunks:
        if not speaking:  # Speech interrupted
            logger.debug("Speech interrupted before speaking the next chunk.")
            break
        
        chunk = chunk.strip()
        if chunk:  # Only speak non-empty chunks
            try:
                yapper.yap(chunk + '.', block=True)  # Adding period back for natural pauses
                logger.debug(f"Spoken chunk: {chunk}")
            except Exception as e:
                logger.error(f"Error during speech synthesis: {e}")
                break
        
        if not speaking:
            logger.debug("Speech interrupted after speaking the chunk.")
            break
    
    speaking = False
    logger.info("Speech synthesis completed or interrupted.")

def change_voice(voice: PiperVoice = PiperVoice.AMY, quality: PiperQuality = PiperQuality.MEDIUM):
    """
    Changes the voice used by the TTS system.
    
    Args:
        voice (PiperVoice): The voice to use from PiperVoice enum
        quality (PiperQuality): The quality level from PiperQuality enum
    """
    global yapper
    try:
        speaker = PiperSpeaker(voice=voice, quality=quality)
        yapper = Yapper(speaker=speaker, plain=True)
        logger.info(f"Voice changed to {voice.value} with {quality.value} quality")
        return True
    except Exception as e:
        logger.error(f"Failed to change voice: {e}")
        return False