from yapper.speaker import BaseSpeaker
import os
import subprocess
import pygame
from yapper.enums import PiperVoice, PiperQuality
from yapper.utils import APP_DIR, get_random_name, install_piper, download_piper_model

class CustomPiperSpeaker(BaseSpeaker):
    def __init__(
        self,
        voice: PiperVoice = PiperVoice.AMY,
        quality: PiperQuality = PiperQuality.MEDIUM,
        speed: float = 1.0,  # New parameter for speed control
    ):
        """
        Speaks the text using piper with speed control.

        Parameters
        ----------
        voice : str, optional
            Name of the piper voice to be used (default: PiperVoice.AMY)
        quality : str, optional
            Quality of the voice (default: PiperQuality.MEDIUM)
        speed : float, optional
            Speed multiplier for speech rate (default: 1.0)
            Values > 1.0 make speech faster
            Values < 1.0 make speech slower
            Example: 0.8 for 20% slower, 1.2 for 20% faster
        """
        assert voice in PiperVoice, f"voice must be one of {', '.join(PiperVoice)}"
        assert quality in PiperQuality, f"quality must be one of {', '.join(PiperQuality)}"
        assert 0.1 <= speed <= 3.0, "speed must be between 0.1 and 3.0"
        
        install_piper()
        self.exe_path = str(
            APP_DIR / "piper" / ("piper.exe" if os.name == "nt" else "piper")
        )
        self.onnx_f, self.conf_f = download_piper_model(voice.value, quality.value)
        self.onnx_f, self.conf_f = str(self.onnx_f), str(self.conf_f)
        self.speed = speed
        pygame.mixer.init()

    def say(self, text: str):
        """Speaks the given text at the specified speed"""
        f = APP_DIR / f"{get_random_name()}.wav"
        
        # Added --length-scale parameter for speed control
        # length_scale is inverse of speed (0.8 length = 1.25x speed)
        length_scale = 1.0 / self.speed
        
        subprocess.run(
            [
                self.exe_path,
                "-m", self.onnx_f,
                "-c", self.conf_f,
                "-f", str(f),
                "--length-scale", str(length_scale),  # New parameter
                "-q",
            ],
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
        )
        
        sound = pygame.mixer.Sound(f)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
        os.remove(f)