from yapper import Yapper, PiperSpeaker, PiperVoice, PiperQuality
import logging
import sys
import os
from datetime import datetime
from pynput import keyboard
import threading
import re

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
        # logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/blindsight_{timestamp}.log"),
        logging.FileHandler(f"logs/blindsight_TTS_latest.log"),

    ]
)

# Create logger for the specific module
logger = logging.getLogger(__name__)
logger.info(f"Logging initialized for {__name__}")

# Speech rate settings
DEFAULT_SPEED = 1.0
MIN_SPEED = 0.5
MAX_SPEED = 2.0
current_speed = DEFAULT_SPEED

# File extension pronunciation dictionary
EXTENSION_PRONUNCIATION = {
    '.txt': 'dot text',
    '.py': 'dot pie',
    '.ipynb': 'dot eye pie notebook',
    '.md': 'dot markdown',
    '.json': 'dot jason',
    '.yaml': 'dot yaml',
    '.yml': 'dot yaml',
    '.csv': 'dot see ess vee',
    '.docx': 'dot doc x',
    '.xlsx': 'dot excel x',
    '.pdf': 'dot pee dee eff',
    '.wav': 'dot wave',
    '.mp3': 'dot em pee three',
    '.mp4': 'dot em pee four',
    '.jpg': 'dot jay peg',
    '.jpeg': 'dot jay peg',
    '.png': 'dot ping',
    '.gif': 'dot gif',
    '.html': 'dot html',
    '.css': 'dot see ess ess',
    '.js': 'dot javascript',
    '.cpp': 'dot see plus plus',
    '.h': 'dot header',
    '.exe': 'dot executable',
    '.log': 'dot log',
    '.zip': 'dot zip',
    '.tar': 'dot tar',
    '.gz': 'dot gee zip',
    '.env': 'dot env',
}

# Initialize Yapper with PiperSpeaker for better quality
try:
    speaker = PiperSpeaker(
        voice=PiperVoice.AMY,
        quality=PiperQuality.MEDIUM
    )
    yapper = Yapper(speaker=speaker, plain=True)
    logger.info("Yapper TTS initialized successfully with PiperSpeaker")
except Exception as e:
    logger.error(f"Failed to initialize Yapper with PiperSpeaker: {e}")
    yapper = Yapper(plain=True)
    logger.info("Falling back to default Yapper speaker")

# Global flag for speech interruption
speaking = False

def on_press(key):
    global speaking
    logger.info("Interrupt signal received. Stopping speech.")
    speaking = False
    return False

def preprocess_text(text):
    """
    Preprocesses text to improve pronunciation of filenames and extensions.
    
    Args:
        text (str): Text to preprocess
    
    Returns:
        str: Processed text with improved pronunciation
    """
    # Function to replace extensions in a filename
    def replace_extension(match):
        filename = match.group(0)
        for ext, pronunciation in EXTENSION_PRONUNCIATION.items():
            if filename.lower().endswith(ext):
                base = filename[:-len(ext)]
                return f"{base} {pronunciation}"
        return filename

    # Find filenames (words containing dots) and replace their extensions
    processed = re.sub(r'\b\w+\.[A-Za-z0-9]+\b', replace_extension, text)
    return processed

def set_speed(speed):
    """
    Sets the speech rate within allowed bounds.
    
    Args:
        speed (float): Desired speech rate multiplier (0.5 to 2.0)
    
    Returns:
        float: Actual speed set
    """
    global current_speed
    current_speed = max(MIN_SPEED, min(MAX_SPEED, speed))
    logger.info(f"Speech rate set to {current_speed}x")
    return current_speed

def speak(text, speed=None):
    """
    Speaks the provided text using Yapper TTS with support for interruption.
    
    Args:
        text (str): The text to be spoken
        speed (float, optional): Speech rate multiplier (0.5 to 2.0)
    """
    global speaking, current_speed
    
    # Set speed if provided
    if speed is not None:
        set_speed(speed)
    
    speaking = True
    processed_text = preprocess_text(text)
    
    # Create a thread for the keyboard listener
    def keyboard_listener():
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    
    listener_thread = threading.Thread(target=keyboard_listener)
    listener_thread.daemon = True
    listener_thread.start()
    logger.debug("Keyboard listener thread started.")
    
    # Split text into sentences or chunks for more responsive interruption
    chunks = processed_text.split('.')
    
    for chunk in chunks:
        if not speaking:
            logger.debug("Speech interrupted before speaking the next chunk.")
            break
        
        chunk = chunk.strip()
        if chunk:
            try:
                # Note: The current version of Yapper doesn't support speed control directly
                # This is a placeholder for when it's implemented
                yapper.yap(chunk + '.', block=True)
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