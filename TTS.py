import pyttsx3
import logging
import sys
import os
from datetime import datetime

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

# Test logging
logger.info(f"Logging initialized for {__name__}")
engine = pyttsx3.init()

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def speak(text):
    """
    Speaks the provided text using the pyttsx3 engine.
    
    Parameters:
        engine (pyttsx3.Engine): The TTS engine.
        text (str): Text to be spoken.
    """
    try:
        engine.say(text)
        engine.runAndWait()
        logger.info("Speech completed successfully.")
    except Exception as e:
        # print(f"An error occurred during speech: {e}")
        logger.error(f"An error occurred during speech: {e}")