import time
import threading
from config import CONFIG, get_save_path
from tts import configure_tts, speak
from chains import create_chains
from conversation import ConversationManager
import speech_recognition as sr
import trigger_detection
import logging

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

def llm_process(msg):
    conversation.add_message(msg)
    logging.info("Sending text to LLM")

def listen_background():
    """Continuous background listening.

    This function continuously listens for audio input from the microphone and puts the captured audio
    into a list for further processing.
    """
    logging.info("Starting background listening...")
    with sr.Microphone() as source:
        while True:
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
audio_thread = threading.Thread(target=listen_background, args=())

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.lang import Builder

Builder.load_string('''
<MainWindow>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    BoxLayout:
        size_hint: 1, 0.1
        spacing: 10

        Button:
            id: listen_btn
            text: 'Start Listening'
            on_press: root.toggle_listening()

        Button:
            text: 'Settings'
            size_hint: 0.3, 1
            on_press: root.open_settings()

    ScrollView:
        size_hint: 1, 0.7

        Label:
            id: chat_log
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            halign: 'left'
            valign: 'top'
            padding: 10, 10

<SettingsDialog>:
    title: 'Trigger Words & Emotion Thresholds'
    size_hint: 0.8, 0.8

    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10

        Label:
            text: 'Trigger Words (comma-separated):'
            size_hint_y: None
            height: 30

        TextInput:
            id: trigger_words_input
            size_hint_y: None
            height: 60

        GridLayout:
            cols: 3
            spacing: 10
            size_hint_y: 0.6

            Label:
                text: 'Emotion'
                bold: True
            Label:
                text: 'Threshold'
                bold: True
            Label:
                text: 'Value'
                bold: True

            # Emotion sliders
            Label:
                text: 'Sadness'
            Slider:
                id: sadness_slider
                min: 0
                max: 1
                step: 0.05
            Label:
                id: sadness_value
                text: '{:.2f}'.format(sadness_slider.value)

            # Repeat for other emotions...
            # [Similar blocks for joy, love, anger, fear, surprise]

            Label:
                text: 'Joy'
            Slider:
                id: joy_slider
                min: 0
                max: 1
                step: 0.05
            Label:
                id: joy_value
                text: '{:.2f}'.format(joy_slider.value)

            Label:
                text: 'Love'
            Slider:
                id: love_slider
                min: 0
                max: 1
                step: 0.05
            Label:
                id: love_value
                text: '{:.2f}'.format(love_slider.value)

            Label:
                text: 'Anger'
            Slider:
                id: anger_slider
                min: 0
                max: 1
                step: 0.05
            Label:
                id: anger_value
                text: '{:.2f}'.format(anger_slider.value)
                
            Label:
                text: 'Fear'
            Slider:
                id: fear_slider
                min: 0
                max: 1
                step: 0.05
            Label:
                id: fear_value
                text: '{:.2f}'.format(fear_slider.value)

            Label:
                text: 'Surprise'
            Slider:
                id: surprise_slider
                min: 0
                max: 1
                step: 0.05
            Label:
                id: surprise_value
                text: '{:.2f}'.format(surprise_slider.value)

        Button:
            text: 'Save'
            size_hint_y: None
            height: 40
            on_press: root.save_settings()
''')

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = {
            'trigger_words': trigger_detector.settings.trigger_phrases,
            'thresholds': trigger_detector.settings.emotion_thresholds
        }

    def toggle_listening(self):
        if self.ids.listen_btn.text == 'Start Listening':
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.ids.listen_btn.text = 'Stop Listening'
        audio_thread.start()

    def stop_listening(self):
        self.ids.listen_btn.text = 'Start Listening'
        quit()

    def open_settings(self):
        Factory.SettingsDialog().open()

    def update_chat(self, message):
        self.ids.chat_log.text += f'\n{message}'
        self.ids.chat_log.height = self.ids.chat_log.texture_size[1]


class SettingsDialog(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_app = App.get_running_app().root
        self.ids.trigger_words_input.text = ', '.join(main_app.settings['trigger_words'])

        # Initialize sliders with current values
        for emotion in main_app.settings['thresholds']:
            slider = self.ids[f'{emotion}_slider']
            slider.value = main_app.settings['thresholds'][emotion]

    def save_settings(self):
        main_app = App.get_running_app().root
        trigger_detector.settings.trigger_phrases = [
            word.strip() for word in self.ids.trigger_words_input.text.split(',')
        ]

        for emotion in main_app.settings['thresholds']:
            slider = self.ids[f'{emotion}_slider']
            trigger_detector.settings.emotion_thresholds[emotion] = slider.value

        self.dismiss()

class MemoryMateApp(App):
    def build(self):
        return MainWindow()

try:
    MemoryMateApp().run()
except KeyboardInterrupt:
    logging.info("Shutting down...")
    audio_thread.join()