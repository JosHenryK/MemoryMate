import speech_recognition as sr
import pyttsx3
import time
import logging
from transformers import pipeline

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

#initialize trigger detection
trigger_classifier = pipeline("text-classification", model="Panda0116/emotion-classification-model")
trigger_emotions = {
    #anger
    'LABEL_3' : 0.8,

    #fear
    'LABEL_4' : 0.8,

    #suprise
    'LABEL_5': 0.95
}

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
            audio = recognizer.listen(source, phrase_time_limit=10)  # 5 seconds

            # Recognize speech using Google's speech recognition
            logging.info("Processing audio...")
            recognized_text = recognizer.recognize_google(audio).lower()
            logging.info(f"{recognized_text}")

            # Check for exit command
            if recognized_text in ["exit", "stop", "quit"]:
                logging.info("Exiting program...")
                speak_text("Goodbye!")
                return False

            emotions = trigger_classifier(recognized_text)
            for emotion in emotions:
                if emotion['label'] in trigger_emotions:
                    min_score = trigger_emotions[emotion['label']]
                    if emotion['score'] > min_score:
                        logging.info(f"Dementia detection triggered. Magnitude {emotion['score']}.")

                        #process stuff related to handling dementia episodes
                    else:
                        logging.info(f"Insufficient emotion detected {emotion['label']} at magnitude {emotion['score']}.")
                else:
                    logging.info(f"Invalid emotion detected {emotion['label']}.")

            # Speak the recognized text
            speak_text(recognized_text)
            return True

    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service: {e}")
    except sr.UnknownValueError:
        logging.warning("Sorry, I could not understand what you said.")
    #except Exception as e:
    #    logging.error(f"An error occurred: {e}")

    return True

def main():
    """Main function to run the speech-to-text and text-to-speech loop."""
    logging.info("Starting speech-to-text and text-to-speech program...")
    speak_text("Hello! I am ready to listen.")

    running = True
    while running:
        running = listen_and_recognize()

if __name__ == "__main__":
    main()