# Python program to translate speech to text and text to speech

import speech_recognition as sr
import pyttsx3

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def speak_text(command):
    """Convert text to speech."""
    engine.say(command)
    engine.runAndWait()

# Infinite loop for continuous speech-to-text and text-to-speech
while True:
    try:
        # Use the microphone as the source for input
        with sr.Microphone() as source:
            # Adjust for ambient noise and listen for user input
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.listen(source)

            # Recognize speech using Google's speech recognition
            recognized_text = recognizer.recognize_google(audio).lower()
            print(f"Did you say: {recognized_text}")

            # Speak the recognized text
            speak_text(recognized_text)

    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service: {e}")

    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")