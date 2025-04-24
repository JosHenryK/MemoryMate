import sys
import os
from unittest.mock import Mock, patch
import pytest

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio import setup_recognizer, listen_background, audio_queue

@pytest.fixture

#Creates a mock recognizer object for testing purposes. This fixture provides a mock instance of a recognizer, with the adjust_for_ambient_noise` method mocked, to be used in tests that require a recognizer object.
#Returns: Mock: A mock object simulating a recognizer with an adjust_for_ambient_noise method.
def mock_recognizer():
    recognizer = Mock()
    recognizer.adjust_for_ambient_noise = Mock()
    return recognizer

#Test the setup_recognizer function to ensure it initializes the recognizer and adjusts for ambient noise.
#Parameters: mock_recognizer (Mock): A mock recognizer object with the adjust_for_ambient_noise` method mocked.
#Returns: None
def test_setup_recognizer(mock_recognizer):
    with patch('audio.sr.Recognizer', return_value=mock_recognizer):
        result = setup_recognizer()
        result.adjust_for_ambient_noise.assert_called_once()

@patch('audio.sr.Microphone')

#Test the listen_background function to ensure it processes audio input and handles errors appropriately.
#Parameters: mock_mic (Mock): A mock object for the Microphone class, used to simulate microphone input during testing., caplog (pytest.LogCaptureFixture): A fixture to capture log output during the test, used to verify error logging.
#Returns: None
def test_listen_background(mock_mic, caplog):
    mock_audio = Mock()
    mock_recognizer = Mock()
    mock_recognizer.listen.return_value = mock_audio

    # Test normal operation
    listen_background(mock_recognizer)
    assert audio_queue.qsize() > 0

    # Test error handling
    mock_recognizer.listen.side_effect = Exception("Audio error")
    listen_background(mock_recognizer)
    assert "Audio error" in caplog.text