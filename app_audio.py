import time
import threading
from config import CONFIG, get_save_path
from tts_gui import configure_tts, speak
from chains import create_chains
from conversation import ConversationManager
import speech_recognition as sr
import trigger_detection
import logging
import llm_gui
import streamlit as st

def main():
    """
    Entry point of the application.
    Initializes components, creates dependencies, and starts necessary threads.
    """
    # Initialize components
    logging.basicConfig(level=logging.DEBUG)
    configure_tts()
    
    # Create dependencies
    recognizer = setup_recognizer()
    chains = create_chains()
    conversation = ConversationManager()
    
    # Start threads
    audio_thread = threading.Thread(target=listen_background, args=(recognizer,))
    audio_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        audio_thread.join()

if __name__ == "__main__":
    main()