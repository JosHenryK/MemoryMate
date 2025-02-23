import threading
from tts import speak, tts_worker
from chains import create_chains
from conversation import ConversationManager
import speech_recognition as sr
import trigger_detection
import logging
import flet as ft
import llm
import sys

if __name__ != "__main__":
    quit()

def setup_recognizer():
    """Initialize and configure speech recognizer."""
    recognizer_result = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer_result.adjust_for_ambient_noise(source)
        logging.info(f"Energy threshold set to: {recognizer_result.energy_threshold}")
    return recognizer_result

# Initialize components
logging.basicConfig(level=logging.DEBUG)
stopEvent = threading.Event()

threading.Thread(target=tts_worker, daemon=True).start()

# Create dependencies
recognizer = setup_recognizer()
chains = create_chains()
conversation = ConversationManager()
trigger_detector = trigger_detection.TriggerDetector()

def log_user_rec(msg):
    conversation.add_message(f'ME: {msg}')
    if "print" in page_functions:
        page_functions["print"](f'You: {msg}')
    else:
        logging.error("print function not found in page_functions")

def listen_background():
    """Continuous background listening."""
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
audio_thread = threading.Thread(target=listen_background, daemon=True)
audio_thread.start()

page_functions = {}

# Method to summarize the chat
def summarize_chat():
    summary_prompt = "Please summarize the conversation so far."
    return llm.send_message(summary_prompt).text

# Function to display the summary page
def summary_page(page):
    summary_content = summarize_chat()
    page.controls.clear()
    page.controls.append(ft.Text("Conversation Summary"))
    page.controls.append(ft.Text(summary_content))
    page.update()

def llm_process():
    logging.info("Sending text to LLM")

    result = llm.send_message(conversation.get_conversation_text()).text
    conversation.add_message(f'YOU: {result}')
    if "print" in page_functions:
        page_functions["print"](f'Memory Mate: {result}')
    else:
        logging.error("print function not found in page_functions")
    speak(result)
    conversation.clear()


def home_page(page):
    page.add(
        ft.Column(
            [
                ft.Text(
                    "Welcome to Memory Mate",
                    size=48,
                    weight="bold",
                    color="#f4997c",
                    text_align="center",
                ),
                ft.Image(
                    src="https://example.com/logo.png",  # Replace with your logo URL
                    width=200,
                    height=200,
                    fit="contain",
                ),
                ft.Text(
                    "Your personal assistant to help you remember and manage tasks efficiently.",
                    size=18,
                    color="#ffffff",
                    text_align="center",
                ),
                ft.ElevatedButton(
                    "Get Started",
                    on_click=lambda e: page.go("/chat"),
                    color="white",
                    bgcolor="#f4997c",
                    width=200,
                    height=50,
                )
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=20,
        )
    )

# Global variable to store chat messages
chat_messages = []

def chat_page(page):
    # Chat messages container
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # Load existing chat messages
    for msg in chat_messages:
        chat.controls.append(ft.Text(msg))

    # Message input field
    new_message = ft.TextField(
        hint_text="Type a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        on_submit=lambda e: send_click(e),
        border_color="#f4997c",  # Border color matching the theme
    )

    def print_to_chat(msg):
        chat.controls.append(ft.Text(msg))
        chat_messages.append(msg)  # Store the message in the global variable
        page.update()

    page_functions["print"] = print_to_chat

    def send_click(e):
        if new_message.value.strip():
            log_user_rec(new_message.value.strip())
            llm_process()
            new_message.value = ""
            page.update()

    # Add controls to page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, color="#f4997c"),  # Border color matching the theme
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            controls=[
                new_message,
                ft.ElevatedButton(
                    "Send",
                    on_click=send_click,
                    bgcolor="#f4997c",  # Button background color
                    color="#ffffff",  # Button text color
                ),
            ]
        ),
    )

def settings_page(page):
    def toggle_dark_mode(e):
        page.theme_mode = "dark" if e.control.value else "light"
        page.update()

    def change_language(e):
        selected_language = e.control.value
        # Handle language change logic here
        print(f"Language changed to: {selected_language}")

    page.add(
        ft.Column(
            [
                ft.Text("Settings", size=32, weight="bold", color="#f4997c"),
                ft.Switch(
                    label="Dark Mode",
                    on_change=toggle_dark_mode,
                ),
                ft.Dropdown(
                    label="Language",
                    options=[
                        ft.DropdownOption("English"),
                        ft.DropdownOption("Spanish"),
                        ft.DropdownOption("French"),
                    ],
                    on_change=change_language,
                ),
                ft.Switch(
                    label="Enable Notifications",
                    value=True,
                    on_change=lambda e: print(f"Notifications {'enabled' if e.control.value else 'disabled'}"),
                ),
            ],
            alignment="start",
            spacing=20,
        )
    )

def flet_main(page: ft.Page):
    print("MAIN CALLED")
    page.title = "MemoryMate"
    page.bgcolor = "#483C32"  # Dark gray background color
    page.padding = 20

    # Set the theme with custom colors
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#f4997c",  # Main color
            on_primary="#ffffff",  # Text color on primary
            surface="#ffffff",  # Background color
            on_surface="#000000",  # Text color on surface
        )
    )

    def on_nav_change(e):
        page.controls.clear()
        if e.control.selected_index == 0:
            home_page(page)
        elif e.control.selected_index == 1:
            chat_page(page)
        elif e.control.selected_index == 2:
            settings_page(page)
        elif e.control.selected_index == 3:
            summary_page(page)
        elif e.control.selected_index == 4:
            page.window.close()
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.CHAT, label="Chat"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK, label="Summary"),
            ft.NavigationBarDestination(icon=ft.Icons.EXIT_TO_APP, label="Exit"),
        ],
        bgcolor="#00000",  # Matching theme color
        on_change=on_nav_change,
    )

    home_page(page)  # Default to home page
try:
    ft.app(flet_main)
except KeyboardInterrupt:
    logging.info("Shutting down...")

stopEvent.set()
audio_thread.join()