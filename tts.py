import threading
import logging
import queue
from gtts import gTTS
from playsound import playsound
import os

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

tts_lock = threading.Lock()
tts_queue = queue.Queue()

#Worker thread to process TTS queue
def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        try:
            with tts_lock:
                logging.info(f"Speaking: {text[:50]}...")
                tts = gTTS(text)
                filename = "temp_tts.mp3"
                tts.save(filename)
                playsound(filename)
                os.remove(filename)
        except Exception as e:
            logging.error(f"Speech error: {str(e)}", exc_info=True)
        tts_queue.task_done()

#Add text to TTS queue for speaking
#Args: text (str): The text to be spoken.
def speak(text):
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