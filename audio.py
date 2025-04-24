import speech_recognition as sr
import logging

audio_list = []

#Initialize and configure speech recognizer. This function creates a speech recognizer object and configures it by adjusting for ambient noise. It also logs the energy threshold that is set for the recognizer.
#Returns: recognizer (Recognizer): The configured speech recognizer object.
def setup_recognizer():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        logging.info(f"Energy threshold set to: {recognizer.energy_threshold}")
    return recognizer

#Continuous background listening. This function continuously listens for audio input from the microphone and puts the captured audio into a list for further processing.
#Args: recognizer (Recognizer): The speech recognition object used to capture audio.
def listen_background(recognizer):
    logging.info("Starting background listening...")
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=5)
                audio_list.append(audio)
                logging.debug(f"Audio captured, list size: {len(audio_list)}")
            except Exception as e:
                logging.error(f"Listening error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Test audio capture
    logging.basicConfig(level=logging.DEBUG)
    r = setup_recognizer()
    listen_background(r)