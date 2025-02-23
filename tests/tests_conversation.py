import pytest
from conversation import ConversationManager

@pytest.fixture
def conv_manager():
    return ConversationManager()

def test_add_message(conv_manager):
    conv_manager.add_message("Test message")
    assert len(conv_manager.history) == 1
    assert "Test message" in conv_manager.get_conversation_text()

def test_clear_conversation(conv_manager):
    conv_manager.add_message("Test")
    conv_manager.clear()
    assert len(conv_manager.history) == 0

def test_activity_state(conv_manager):
    conv_manager.set_active(True)
    assert conv_manager.active is True
    conv_manager.set_active(False)
    assert conv_manager.active is False

def test_history_rotation():
    manager = ConversationManager()
    for i in range(20):
        manager.add_message(f"Message {i}")
    assert len(manager.history) == 15