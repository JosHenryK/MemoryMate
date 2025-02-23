import os
import logging
import trigger_detection
import time
import threading
import speech_recognition as sr
import pyttsx3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Google API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("The GOOGLE_API_KEY environment variable is not set.")

# Initialize the LLM (Google Gemini Pro in this case)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

# Define the summarization prompt
summarization_prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant that summarizes conversations in real time.
    Given the following conversation, provide a concise summary of the key points:

    Conversation:
    {conversation}

    Summary:
    """
)

# Create a chain for summarization
summarization_chain = summarization_prompt | llm | StrOutputParser()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

#initialize trigger detection
trigger_detector = trigger_detection.TriggerDetector()

# Customize the text-to-speech engine
def configure_tts():
    """Configure the text-to-speech engine."""
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Change index to switch voices
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

configure_tts()

def speak_text(command):
    """Convert text to speech."""
    logging.info(f"Speaking: {command}")
    engine.say(command)
    engine.runAndWait()

def listen_and_recognize():
    """Listen to the microphone and recognize speech."""
    try:
        with sr.Microphone() as source:
            # Dynamically adjust for ambient noise
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            logging.info(f"Energy threshold set to: {recognizer.energy_threshold}")

            logging.info("Listening...")
            time.sleep(0.5)  # Short delay to stabilize
            audio = recognizer.listen(source, phrase_time_limit=10)  # 10 seconds

            # Recognize speech using Google's speech recognition
            logging.info("Processing audio...")
            recognized_text = recognizer.recognize_google(audio).lower()
            logging.info(f"Recognized: {recognized_text}")

            # Check for exit command
            if recognized_text in ["exit", "stop", "quit"]:
                logging.info("Exiting program...")
                speak_text("Goodbye!")
                return False, recognized_text

            return trigger_detector.detect(recognized_text), recognized_text

    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service: {e}")
    except sr.UnknownValueError:
        logging.warning("Sorry, I could not understand what you said.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    return True, ""

def real_time_summarizer():
    conversation = []  # Store the conversation history
    speak_text("Hello! I am ready to listen.")
    running = True

    while running:
        running, new_input = listen_and_recognize()
        if new_input:
            conversation.append(f"You: {new_input}")
            full_conversation = "\n".join(conversation)

            # Generate the summary
            summary = summarization_chain.invoke({"conversation": full_conversation})
            logging.info(f"Summary: {summary}")
            speak_text(f"Summary: {summary}")

if __name__ == "__main__":
    real_time_summarizer()