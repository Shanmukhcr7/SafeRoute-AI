import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class VoiceAssistant:
    """Simulates voice alerts for the ADAS HMI using pyttsx3."""
    
    def __init__(self, simulate_only=True):
        self.simulate_only = simulate_only
        if not self.simulate_only:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)
            except ImportError:
                logging.warning("pyttsx3 not installed. Defaulting to simulated voice logs.")
                self.simulate_only = True
                
    def speak(self, text: str):
        """Speaks the text or logs it if in simulation mode."""
        if self.simulate_only:
            logging.info(f"🔊 [VOICE]: {text}")
        else:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logging.error(f"Voice engine failed: {e}")
