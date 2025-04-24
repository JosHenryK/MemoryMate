import pytest
from unittest.mock import Mock, patch
from tts_gui import configure_tts, speak

@pytest.fixture
def mock_engine():
    engine = Mock()
    engine.getProperty.return_value = [Mock(id=0)]
    engine.setProperty = Mock()
    return engine

@patch('tts.engine')
def test_configure_tts(mock_engine):
    configure_tts()
    mock_engine.getProperty.assert_called_with('voices')
    mock_engine.setProperty.assert_any_call('voice', mock_engine.getProperty.return_value[0].id)
    mock_engine.setProperty.assert_any_call('rate', 160)

def test_speak_thread_safety():
    with patch('tts.tts_lock') as mock_lock:
        speak("Test message")
        mock_lock.__enter__.assert_called_once()

def test_speak_error_handling(caplog):
    with patch('tts.engine.say', side_effect=Exception("TTS error")):
        speak("Bad message")
        assert "TTS error" in caplog.text