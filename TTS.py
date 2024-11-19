import pyttsx3
import logging

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
        logging.info("Speech completed successfully.")
    except Exception as e:
        # print(f"An error occurred during speech: {e}")
        logging.error(f"An error occurred during speech: {e}")