import pyttsx3
import threading
import logging

# Initialize TTS engine
engine = pyttsx3.init()
tts_lock = threading.Lock()

def configure_tts():
    """Configure text-to-speech engine"""
    logging.debug("Configuring TTS engine...")
    try:
        voices = engine.getProperty('voices')
        logging.debug(f"Available voices: {[v.name for v in voices]}")
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.9)
        logging.info(f"TTS configured with voice: {voices[0].name}")
        
        # Test voice immediately
        engine.say("TTS initialization test")
        engine.runAndWait()
    except Exception as e:
        logging.error(f"TTS configuration failed: {e}", exc_info=True)

def speak(text):
    """Thread-safe text-to-speech with queue.

    Args:
        text (str): The text to be spoken.

    """
    try:
        with tts_lock:
            logging.info(f"Speaking: {text[:50]}...")
            engine = pyttsx3.init()  # Reinitialize engine in thread
            engine.say(text)
            engine.runAndWait()
            engine.stop()  # Explicitly stop the engine
    except Exception as e:
        logging.error(f"Speech error: {str(e)}", exc_info=True)
            
    threading.Thread(target=speak, daemon=True).start()

if __name__ == "__main__":
    # Test TTS independently
    configure_tts()
    speak("This is a test of the text-to-speech system")