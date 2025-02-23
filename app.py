import time
import threading
from config import CONFIG, get_save_path
from tts import configure_tts, speak
from chains import create_chains
from conversation import ConversationManager
import speech_recognition as sr
import trigger_detection
import logging

if __name__ != "__main__":
    quit()

def setup_recognizer():
    """Initialize and configure speech recognizer.

    This function creates a speech recognizer object and configures it by adjusting for ambient noise.
    It also logs the energy threshold that is set for the recognizer.

    Returns:
        recognizer (Recognizer): The configured speech recognizer object.
    """
    recognizer_result = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer_result.adjust_for_ambient_noise(source)
        logging.info(f"Energy threshold set to: {recognizer_result.energy_threshold}")
    return recognizer_result

# Initialize components
logging.basicConfig(level=logging.DEBUG)
configure_tts()

# Create dependencies
recognizer = setup_recognizer()

chains = create_chains()
conversation = ConversationManager()
trigger_detector = trigger_detection.TriggerDetector()

def listen_background():
    """Continuous background listening.

    This function continuously listens for audio input from the microphone and puts the captured audio
    into a list for further processing.
    """
    logging.info("Starting background listening...")
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=5)
                logging.info("Processing audio...")
                recognized_text = recognizer.recognize_google(audio).lower()
                logging.info(f"{recognized_text}")

                if trigger_detector.detect(recognized_text):
                    logging.info("Sending text to LLM")
                    conversation.add_message(recognized_text)

            except Exception as e:
                logging.error(f"Listening error: {str(e)}", exc_info=True)

# Start threads
audio_thread = threading.Thread(target=listen_background, args=())
audio_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Shutting down...")
    audio_thread.join()