@patch('audioProcessor.summary_chain.invoke')
@patch('audioProcessor.save_summary')
@patch('audioProcessor.speak')
def test_generate_full_summary_success(mock_speak, mock_save_summary, mock_invoke):
    # Mock the return value of the summary chain
    mock_invoke.return_value = "This is a generated summary."

    # Mock the save_summary function to return a fake path
    mock_save_summary.return_value = "/fake/path/summary.txt"

    # Set up a sample conversation
    conversation.extend([
        "User: Hello, how are you?",
        "Assistant: I'm good, thank you! How can I help you today?",
        "User: I need help with my project."
    ])

    # Call the function to test
    generate_full_summary()

    # Assertions
    mock_invoke.assert_called_once_with({"conversation": "\n".join(conversation)})
    mock_save_summary.assert_called_once_with("This is a generated summary.")
    mock_speak.assert_called_once_with(
        "Full summary ready. I've saved it for you. Here's the overview: This is a generated summary."
    )