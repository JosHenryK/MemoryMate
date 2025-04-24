import threading
import logging
import queue
from gtts import gTTS
from playsound import playsound
import os

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

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
    # Start worker thread
    threading.Thread(target=tts_worker, daemon=True).start()

    # Test TTS independently
    speak("This is a test of the text-to-speech system")
    speak("This is another test of the text-to-speech system")

    # Keep the main thread alive to allow the worker thread to process the queue
    tts_queue.join()