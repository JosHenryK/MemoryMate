import threading
import logging
import queue
import pyttsx3

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

tts_lock = threading.Lock()
tts_queue = queue.Queue()

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Set properties for Australian male voice
voices = engine.getProperty('voices')
for voice in voices:
    if 'en-au' in voice.id and 'male' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

def tts_worker():
    """Worker thread to process TTS queue"""
    while True:
        text = tts_queue.get()
        if text is None:
            break
        try:
            with tts_lock:
                logging.info(f"Speaking: {text[:50]}...")
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            logging.error(f"Speech error: {str(e)}", exc_info=True)
        tts_queue.task_done()

def speak(text):
    """Add text to TTS queue for speaking

    Args:
        text (str): The text to be spoken.

    """
    logging.debug(f"Queueing text for speech: {text}")
    tts_queue.put(text)

if __name__ == "__main__":
    # Start worker thread
    threading.Thread(target=tts_worker, daemon=True).start()

    # Test TTS independently
    speak("This is a test of the text-to-speech system")
    speak("This is another test of the text-to-speech system")

    # Keep the main thread alive to allow the worker thread to process the queue
    tts_queue.join()