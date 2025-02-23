import unittest
from unittest.mock import patch, MagicMock

with patch.dict('sys.modules', {
    'langchain_google_genai': MagicMock(),
    'langchain_core.prompts': MagicMock(),
    'langchain_core.output_parsers': MagicMock()
}):
    from proto_LLM import real_time_summarizer

class TestRealTimeSummarizer(unittest.TestCase):

    @patch('proto_LLM.summarization_chain')
    def test_real_time_summarizer(self, mock_summarization_chain):
        mock_summarization_chain.return_value = "This is a summary."
        conversation = [
            "User: Hello, how are you?",
            "Assistant: I'm good, thank you! How can I help you today?",
            "User: I need help with my project."
        ]
        summary = real_time_summarizer(conversation)
        self.assertEqual(summary, "This is a summary.")
        mock_summarization_chain.assert_called_once_with(conversation=conversation)

if __name__ == '__main__':
    unittest.main()