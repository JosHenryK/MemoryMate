from collections import deque
import logging
from config import CONFIG

class ConversationManager:
    """
    Manages the conversation history and state of a conversation.
    """

    def __init__(self):
        self.history = []
        self.active = False
        
    def add_message(self, text):
        """
        Adds a user message to the conversation history.

        Args:
            text (str): The user message to add.
        """
        self.history.append(f"User: {text}")
        logging.debug(f"Added message: {text}")

        if len(self.history) > 10:
            self.history.pop(0)
            logging.debug(f"Removed first message. Exceed max history length.");
        
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
        return f"This is a conversation between a me and you.\n{"\n".join(self.history)}\nYOU:"
    
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
    print(cm.get_conversation_text())