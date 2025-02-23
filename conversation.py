from collections import deque
import logging
from config import CONFIG

class ConversationManager:
    """
    Manages the conversation history and state of a conversation.
    """

    def __init__(self):
        self.history = deque(maxlen=CONFIG["max_history"])
        self.active = False
        
    def add_message(self, text):
        """
        Adds a user message to the conversation history.

        Args:
            text (str): The user message to add.
        """
        self.history.append(f"User: {text}")
        logging.debug(f"Added message: {text}")
        
    def clear(self):
        """
        Clears the conversation history.
        """
        self.history.clear()
        logging.warning("Conversation history cleared")
        
    def get_conversation_text(self):
        """
        Returns the conversation history as a formatted text.

        Returns:
            str: The conversation history.
        """
        return "\n".join(self.history)
    
    def set_active(self, state):
        """
        Sets the active state of the conversation.

        Args:
            state (bool): The active state of the conversation.
        """
        self.active = state
        logging.info(f"Conversation active: {state}")

if __name__ == "__main__":
    # Test conversation management
    cm = ConversationManager()
    cm.add_message("Test message")
    cm.add_message("Another test message")
    cm.add_message("Final test message")
    print(cm.get_conversation_text())