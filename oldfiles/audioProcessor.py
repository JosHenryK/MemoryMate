import os
import logging
import time
import threading
import queue
from collections import deque
import speech_recognition as sr
import pyttsx3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Initialize components with thread safety
engine = pyttsx3.init()
tts_lock = threading.Lock()  # Add a lock for TTS operations

# Configure verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load environment variables
load_dotenv()

# Configuration
CONFIG = {
    "max_history": 15,
    "wake_word": "hey recall",
    "summary_command": "summarize",
    "key_points_length": 3,
    "save_folder": "summaries"
}

# Initialize components
logging.info("Initializing components...")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
recognizer = sr.Recognizer()
engine = pyttsx3.init()
audio_queue = queue.Queue()
conversation = deque(maxlen=CONFIG["max_history"])
active = threading.Event()

# Create save directory
os.makedirs(CONFIG["save_folder"], exist_ok=True)
logging.debug(f"Created save directory at {CONFIG['save_folder']}")

# Prompt templates
key_points_prompt = ChatPromptTemplate.from_template(
    """Identify {num_points} MOST IMPORTANT key points from this conversation. 
    Respond ONLY with bullet points, no explanations. Be very selective:
    
    {conversation}"""
)

summary_prompt = ChatPromptTemplate.from_template(
    """Create a comprehensive summary of this conversation for someone with memory loss.
    Include chronological order, key decisions, and important details. Use simple language:
    
    {conversation}"""
)

# Chains
key_points_chain = key_points_prompt | llm | StrOutputParser()
summary_chain = summary_prompt | llm | StrOutputParser()

def configure_tts():
    """Configure text-to-speech engine"""
    logging.debug("Configuring TTS engine...")
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 0.9)
    logging.info(f"TTS configured with voice: {voices[0].name}")

def save_summary(content):
    """Save summary to timestamped file"""
    filename = f"{int(time.time())}_summary.txt"
    path = os.path.join(CONFIG["save_folder"], filename)
    with open(path, 'w') as f:
        f.write(content)
    logging.info(f"Summary saved to {path}")
    return path

def speak(text):
    """Thread-safe text-to-speech with queue"""
    logging.debug(f"Queueing speech: {text}")
    def _speak():
        try:
            with tts_lock:  # Acquire lock before using TTS
                logging.info(f"Speaking: {text[:50]}...")
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            logging.error(f"Speech error: {str(e)}", exc_info=True)
            
    # Use a daemon thread to prevent hanging
    t = threading.Thread(target=_speak, daemon=True)
    t.start()

def process_audio():
    """Background audio processing thread"""
    logging.info("Starting audio processing thread...")
    while True:
        logging.debug("Waiting for audio from queue...")
        audio = audio_queue.get()
        if audio is None:
            logging.warning("Received exit signal in audio queue")
            break
            
        try:
            logging.debug("Processing audio chunk...")
            text = recognizer.recognize_google(audio).lower()
            logging.info(f"Recognized speech: {text}")
            
            if not active.is_set():
                logging.debug("System inactive - checking for wake word")
                if CONFIG["wake_word"] in text:
                    logging.info("Wake word detected! Activating system...")
                    active.set()
                    speak("How can I help?")
                continue

            logging.debug(f"Active conversation state: {active.is_set()}")
            logging.info(f"Processing command: {text}")

            if text == "exit":
                logging.info("Exit command received")
                active.clear()
                speak("Goodbye!")
            elif text == "clear":
                logging.warning("Clearing conversation history")
                conversation.clear()
                speak("Conversation cleared")
            elif CONFIG["summary_command"] in text:
                logging.info("Summary request received")
                generate_full_summary()
            else:
                logging.debug(f"Adding to conversation: {text}")
                conversation.append(f"User: {text}")
                logging.debug(f"Current conversation length: {len(conversation)}")
                generate_key_points()

        except sr.UnknownValueError:
            logging.warning("Speech recognition could not understand audio")
        except Exception as e:
            logging.error(f"Audio processing error: {str(e)}", exc_info=True)

def generate_key_points():
    """Generate and speak key points"""
    if not conversation:
        logging.warning("Tried to generate key points from empty conversation")
        return
    
    try:
        logging.debug("Generating key points...")
        conv_text = "\n".join(conversation)
        logging.debug(f"Conversation context:\n{conv_text}")
        
        key_points = key_points_chain.invoke({
            "conversation": conv_text,
            "num_points": CONFIG["key_points_length"]
        })
        logging.info(f"Generated key points:\n{key_points}")
        speak(f"Remember: {key_points}")
    except Exception as e:
        logging.error(f"Key points generation failed: {str(e)}", exc_info=True)

def generate_full_summary():
    """Generate and save comprehensive summary"""
    try:
        logging.debug("Generating full summary...")
        conv_text = "\n".join(conversation)
        logging.debug(f"Full conversation context:\n{conv_text}")
        
        summary = summary_chain.invoke({"conversation": conv_text})
        logging.info(f"Generated summary:\n{summary}")
        path = save_summary(summary)
        speak(f"Full summary ready. I've saved it for you. Here's the overview: {summary}")
    except Exception as e:
        logging.error(f"Summary generation failed: {str(e)}", exc_info=True)
        speak("Sorry, I couldn't generate a summary right now")

def listen_background():
    """Continuous background listening"""
    logging.info("Starting background listening thread...")
    with sr.Microphone() as source:
        logging.debug("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        logging.info(f"Current energy threshold: {recognizer.energy_threshold}")
        
        while True:
            try:
                logging.debug("Listening... (CTRL+C to stop)")
                audio = recognizer.listen(source, phrase_time_limit=5)
                logging.debug("Audio captured, adding to queue...")
                audio_queue.put(audio)
                logging.debug(f"Current queue size: {audio_queue.qsize()}")
            except Exception as e:
                logging.error(f"Listening error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    configure_tts()
    logging.info("Starting application...")

    # Start background threads
    logging.debug("Launching processing threads...")
    audio_processor = threading.Thread(target=process_audio)
    listener_thread = threading.Thread(target=listen_background)

    audio_processor.start()
    listener_thread.start()

    try:
        logging.info("Main thread entering sleep loop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.warning("Keyboard interrupt received! Shutting down...")
        audio_queue.put(None)
        audio_processor.join()
        listener_thread.join()
        logging.info("Clean shutdown complete")