import pytest
from unittest.mock import Mock, patch
from app import main

@patch('app.configure_tts')
@patch('app.setup_recognizer')
@patch('app.create_chains')
@patch('app.ConversationManager')
@patch('app.listen_background')
def test_main_app_flow(
    mock_listen, mock_conv, mock_chains,
    mock_setup, mock_tts, caplog
):
    # Mock dependencies
    mock_setup.return_value = Mock()
    mock_chains.return_value = {"test_chain": Mock()}
    mock_conv.return_value = Mock()
    
    # Simulate keyboard interrupt
    with pytest.raises(KeyboardInterrupt):
        main()
    
    # Verify initialization
    mock_tts.assert_called_once()
    mock_setup.assert_called_once()
    mock_chains.assert_called_once()