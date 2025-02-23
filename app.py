import threading
from tts import speak, tts_worker
from chains import create_chains
from conversation import ConversationManager
import speech_recognition as sr
import trigger_detection
import logging
import flet as ft
import llm

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

threading.Thread(target=tts_worker, daemon=True).start()

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

                log_user_rec(recognized_text)
                if trigger_detector.detect(recognized_text):
                    llm_process()
                    print("PROCESSED")

            except Exception as e:
                logging.error(f"Listening error: {str(e)}", exc_info=True)

# Start threads
audio_thread = threading.Thread(target=listen_background, daemon=True)#target=listen_background)
audio_thread.start()

page_functions = {}

def flet_main(page: ft.Page):
    print("MAIN CALLED")
    page.title = "MemoryMate"

    # Chat messages container
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # Message input field
    new_message = ft.TextField(
        hint_text="Type a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        on_submit=lambda e: send_click(e),
    )

    def print_to_chat(msg):
        chat.controls.append(ft.Text(msg))
        page.update()
    page_functions["print"] = print_to_chat

    def send_click(e):
        if new_message.value.strip():
            # Echo the message back to the chat
            log_user_rec(new_message.value.strip())
            llm_process()
            new_message.value = ""
            page.update()

    # Add controls to page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            controls=[
                new_message,
                ft.ElevatedButton("Send", on_click=send_click),
            ]
        ),
    )

def log_user_rec(msg):
    conversation.add_message(f'ME: {msg}')
    page_functions["print"](f'You: {msg}')

def llm_process():
    logging.info("Sending text to LLM")

    result = llm.send_message(conversation.get_conversation_text()).text
    conversation.add_message(f'YOU: {result}')
    page_functions["print"](f'Assistant: {result}')
    speak(result)

try:
    ft.app(flet_main)
except KeyboardInterrupt:
    logging.info("Shutting down...")


stopEvent.set()
audio_thread.join()