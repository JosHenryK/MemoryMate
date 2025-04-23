import time
import threading
from config import CONFIG, get_save_path
from tts import configure_tts, speak
from chains import create_chains
from conversation import ConversationManager
import speech_recognition as sr
import trigger_detection
import logging
import llm
import streamlit as st

# Initialize components
logging.basicConfig(level=logging.DEBUG)
configure_tts()

# Create dependencies
recognizer = sr.Recognizer()
chains = create_chains()
conversation = ConversationManager()
trigger_detector = trigger_detection.TriggerDetector()

# Use a threading event for better control
listening_event = threading.Event()
audio_thread = None

#Initialize and configure speech recognizer.
def setup_recognizer():
    recognizer_result = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer_result.adjust_for_ambient_noise(source)
        logging.info(f"Energy threshold set to: {recognizer_result.energy_threshold}")
    return recognizer_result

#Continuous background listening.
def listen_background():
    logging.info("Starting background listening...")
    with sr.Microphone() as source:
        while listening_event.is_set():  # Check event instead of global variable
            try:
                audio = recognizer.listen(source, phrase_time_limit=5)
                logging.info("Processing audio...")
                recognized_text = recognizer.recognize_google(audio).lower()
                logging.info(f"Recognized: {recognized_text}")

                # Update conversation history
                conversation.add_message(f"User: {recognized_text}")
                st.session_state.conversation_text = conversation.get_conversation_text()

                # Detect trigger and send to LLM
                if trigger_detector.detect(recognized_text):
                    logging.info("Sending text to LLM...")
                    llm_response = llm.send_message(conversation.get_conversation_text())
                    conversation.add_message(f"Gemini: {llm_response}")
                    st.session_state.conversation_text = conversation.get_conversation_text()

            except sr.UnknownValueError:
                logging.warning("Could not understand audio.")
            except Exception as e:
                logging.error(f"Listening error: {str(e)}", exc_info=True)
    
    logging.info("Listening stopped.")

# Streamlit UI
st.title("Real-Time Speech Recognition and Processing")

# Initialize session state for conversation history
if "conversation_text" not in st.session_state:
    st.session_state.conversation_text = ""

# Start/Stop Listening Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Listening"):
        if not listening_event.is_set():
            listening_event.set()  # Set event to start listening
            audio_thread = threading.Thread(target=listen_background, daemon=True)
            audio_thread.start()
            st.success("Listening started...")

with col2:
    if st.button("Stop Listening"):
        if listening_event.is_set():
            listening_event.clear()  # Clear event to stop loop
            st.warning("Listening stopped.")

# Display Conversation History
st.subheader("Conversation History")
conversation_display = st.empty()  # Placeholder for real-time updates

# Update conversation display in real time
if st.session_state.conversation_text:
    conversation_display.text_area("Conversation", value=st.session_state.conversation_text, height=300)

# Status Indicator
if listening_event.is_set():
    st.info("Listening... Speak into the microphone.")
else:
    st.info("Press 'Start Listening' to begin.")

# Emotion Detection and Gemini Response
if st.session_state.conversation_text:
    st.subheader("Emotion Detection and Response")
    if "Gemini:" in st.session_state.conversation_text:
        st.write("**Gemini Response:**")
        st.write(st.session_state.conversation_text.split("Gemini:")[-1].strip())