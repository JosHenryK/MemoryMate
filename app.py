import time
import threading
from config import CONFIG, get_save_path
from tts import configure_tts, speak
from chains import create_chains
from conversation import ConversationManager
import speech_recognition as sr
import trigger_detection
import logging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.lang import Builder

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

stopEvent = threading.Event()
def listen_background():
    """Continuous background listening.

    This function continuously listens for audio input from the microphone and puts the captured audio
    into a list for further processing.
    """
    logging.info("Starting background listening...")
    with sr.Microphone() as source:
        while not stopEvent.is_set():
            try:
                audio = recognizer.listen(source, phrase_time_limit=5)
                logging.info("Processing audio...")
                recognized_text = recognizer.recognize_google(audio).lower()
                logging.info(f"{recognized_text}")

                if trigger_detector.detect(recognized_text):
                    llm_process(recognized_text)

            except Exception as e:
                logging.error(f"Listening error: {str(e)}", exc_info=True)

# Start threads
audio_thread = threading.Thread(target=listen_background, daemon=True)#target=listen_background)

Builder.load_file("gui.kv")

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def toggle_listening(self):
        if self.ids.listen_btn.text == 'Start Listening':
            self.start_listening()
        else:
            self.ids.listen_btn.text = 'Start Listening'
            stopEvent.set()

    def start_listening(self):
        self.ids.listen_btn.text = 'Stop Listening/Quit'
        stopEvent.clear()
        audio_thread.start()

    def open_settings(self):
        Factory.SettingsDialog().open()

    def update_chat(self, message):
        self.ids.chat_log.text += f'\n{message}'
        self.ids.chat_log.height = self.ids.chat_log.texture_size[1]


class SettingsDialog(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_app = App.get_running_app().root
        self.ids.trigger_words_input.text = ', '.join(trigger_detector.settings.trigger_phrases)

        # Initialize sliders with current values
        for emotion in trigger_detector.settings.emotion_thresholds:
            slider = self.ids[f'{emotion}_slider']
            slider.value = trigger_detector.settings.emotion_thresholds[emotion]

    def save_settings(self):
        main_app = App.get_running_app().root
        trigger_detector.settings.trigger_phrases = [
            word.strip() for word in self.ids.trigger_words_input.text.split(',')
        ]

        for emotion in trigger_detector.settings.emotion_thresholds:
            slider = self.ids[f'{emotion}_slider']
            trigger_detector.settings.emotion_thresholds[emotion] = slider.value

        self.dismiss()

class MemoryMateApp(App):
    def build(self):
        self.main = MainWindow()
        return self.main

mainApp = MemoryMateApp()

def llm_process(msg):
    conversation.add_message(msg)
    logging.info("Sending text to LLM")
    mainApp.main.update_chat(msg)

try:
    mainApp.run()
except KeyboardInterrupt:
    logging.info("Shutting down...")
    audio_thread.join()