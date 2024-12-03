from yapper import Yapper, PiperSpeaker, PiperVoice, PiperQuality
import threading
from pynput import keyboard
import re
import json
import os
from log_config import setup_logger
import shutil

# Initialize logger
logger = setup_logger('TTS')

class CustomPiperSpeaker(PiperSpeaker):
    def __init__(self, voice: PiperVoice = PiperVoice.AMY, 
                 quality: PiperQuality = PiperQuality.MEDIUM,
                 length_scale: float = 1.0):
        """
        Custom Piper Speaker with speed control via length_scale.
        """
        super().__init__(voice=voice, quality=quality)
        self.length_scale = length_scale
        self.voice = voice
        self.quality = quality
        self._modify_config()

    def _modify_config(self):
        """Modify Piper config file to adjust speech rate."""
        try:
            # Read the current config with explicit UTF-8 encoding
            with open(self.conf_f, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Create backup if it doesn't exist
            backup_path = str(self.conf_f) + '.backup'
            if not os.path.exists(backup_path):
                with open(self.conf_f, 'r', encoding='utf-8') as src, \
                     open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                logger.info(f"Created config backup at {backup_path}")

            # Modify length_scale
            config['length_scale'] = self.length_scale
            
            # Write modified config with explicit UTF-8 encoding
            with open(self.conf_f, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated Piper config with length_scale: {self.length_scale}")
            
        except Exception as e:
            logger.error(f"Error modifying Piper config: {e}")
            # Attempt to restore from backup if it exists
            backup_path = str(self.conf_f) + '.backup'
            if os.path.exists(backup_path):
                with open(backup_path, 'r', encoding='utf-8') as src, \
                     open(self.conf_f, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                logger.info("Restored config from backup")
            raise  # Re-raise the exception to be handled by caller

class TTSController:
    def __init__(self):
        # Initialize speed settings
        self.default_speed = 1.0
        self.min_speed = 0.5
        self.max_speed = 2.0
        self.current_speed = self.default_speed
        self.voice = PiperVoice.AMY
        self.quality = PiperQuality.MEDIUM

        self.speaking = False
        self.recording = False

        # Initialize CustomPiperSpeaker
        try:
            self._initialize_speaker()
        except Exception as e:
            logger.error(f"Failed to initialize Custom Piper: {e}")
            # Initialize without custom configuration
            self.speaker = PiperSpeaker(
                voice=self.voice,
                quality=self.quality
            )
            self.yapper = Yapper(speaker=self.speaker, plain=True)
            logger.info("Initialized with default speaker configuration")

        # Initialize keyboard listener
        self.keyboard_listener = None
        self._setup_keyboard_listener()

    def _setup_keyboard_listener(self):
        """Initialize keyboard listener for spacebar events."""
        def on_press(key):
            if key == keyboard.Key.space:
                if self.speaking:
                    self.speaking = False
                    logger.info("Speech interrupted by spacebar")
                self.recording = True

        def on_release(key):
            if key == keyboard.Key.space:
                self.recording = False

        try:
            # Stop existing listener if any
            if self.keyboard_listener is not None:
                self.keyboard_listener.stop()

            # Create and start new listener
            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release)
            self.keyboard_listener.start()
            logger.info("Keyboard listener initialized")
        except Exception as e:
            logger.error(f"Failed to setup keyboard listener: {e}")

    def _initialize_speaker(self):
        """Initialize or reinitialize the custom speaker."""
        self.speaker = CustomPiperSpeaker(
            voice=self.voice,
            quality=self.quality,
            length_scale=1.0 / self.current_speed  # Inverse relationship
        )
        self.yapper = Yapper(speaker=self.speaker, plain=True)
        logger.info("Custom Piper TTS initialized successfully")

    def set_speed(self, speed=None):
        """Set the speech rate and update Piper configuration."""
        if speed is None:
            speed = self.default_speed
            
        self.current_speed = max(self.min_speed, min(self.max_speed, speed))
        
        try:
            self._initialize_speaker()
            logger.info(f"Speech rate set to {self.current_speed}x")
        except Exception as e:
            logger.error(f"Failed to update speech rate: {e}")
        
        return self.current_speed

    def speak(self, text, speed=None):
        """
        Speaks text with support for interruption and speed control.
        
        Args:
            text (str): Text to be spoken
            speed (float, optional): Speed multiplier (0.5 to 2.0)
        """
        if speed is not None and speed != self.current_speed:
            self.set_speed(speed)
            
        self.speaking = True
        chunks = text.split('.')
        
        for chunk in chunks:
            if not self.speaking:
                logger.info("Speech interrupted")
                break
                
            chunk = chunk.strip()
            if chunk:
                try:
                    self.yapper.yap(chunk + '.', block=True)
                    logger.debug(f"Spoken chunk at speed {self.current_speed}x")
                except Exception as e:
                    logger.error(f"Error during speech synthesis: {e}")
                    break
                
            if not self.speaking:
                logger.debug("Speech interrupted after chunk")
                break

        self.speaking = False
        logger.info("Speech completed or interrupted")

    def is_recording(self):
        """Check if system is currently in recording mode"""
        return self.recording

    def get_current_speed(self):
        """Get current speech rate"""
        return self.current_speed

# Create global TTS controller instance
tts_controller = TTSController()

# Global interface functions
def speak(text, speed=None):
    """Speak text at specified speed"""
    tts_controller.speak(text, speed)

def set_speed(speed):
    """Set speech rate"""
    return tts_controller.set_speed(speed)

def get_speed():
    """Get current speech rate"""
    return tts_controller.get_current_speed()

def is_recording():
    """Check recording status"""
    return tts_controller.is_recording()