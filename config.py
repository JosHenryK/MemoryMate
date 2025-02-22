import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Application configuration
CONFIG = {
    "max_history": 15,
    "wake_word": "hey recall",
    "summary_command": "summarize",
    "key_points_length": 3,
    "save_folder": "summaries"
}

# LLM Configuration
# chains.py
LLM_CONFIG = {
    'model_name': 'memoryMate',
    'temperature': 0.7,
    'model': 'gemini-1.5-flash'  # Add this line with the appropriate model name
}

# Path configuration
def get_save_path():
    """
    Returns the save folder path specified in the CONFIG dictionary.
    If the folder doesn't exist, it will be created.
    """
    os.makedirs(CONFIG["save_folder"], exist_ok=True)
    return CONFIG["save_folder"]