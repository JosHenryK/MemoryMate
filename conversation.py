from collections import deque
import logging
from config import CONFIG

#Manages the conversation history and state of a conversation.
class ConversationManager:
    def __init__(self):
        self.history = []
        self.active = False
    
    #Adds a user message to the conversation history.
    #Args: text (str): The user message to add.
    def add_message(self, text):
        self.history.append(f"User: {text}")
        logging.debug(f"Added message: {text}")

        if len(self.history) > 10:
            self.history.pop(0)
            logging.debug(f"Removed first message. Exceed max history length.");
        
    #Clears the conversation history.
    def clear(self):
        self.history.clear()
        logging.warning("Conversation history cleared")
        
    #Returns the conversation history as a formatted text.
    #Returns: str: The conversation history.
    def get_conversation_text(self):
        return f"This is a conversation between a me and you.\n{"\n".join(self.history)}\nYOU:"
    
    #Sets the active state of the conversation.
    #Args: state (bool): The active state of the conversation.
    def set_active(self, state):
        self.active = state
        logging.info(f"Conversation active: {state}")


# Test conversation management
if __name__ == "__main__":
    cm = ConversationManager()
    cm.add_message("Test message")
    cm.add_message("Another test message")
    cm.add_message("Final test message")
    print(cm.get_conversation_text())