import unittest
from unittest.mock import MagicMock, patch

from src.libs.ask_webllm import ask_web_llm


class TestAskWebLLM(unittest.TestCase):
    @patch("src.libs.ask_webllm.OpenAI")
    @patch("src.libs.ask_webllm.os")
    def test_ask_web_llm(self, mock_os, mock_openai):
        mock_os.getenv.return_value = "test_api_key"

        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client_instance.chat.completions.create.return_value = mock_response

        content = "This is a test.\n <-- ask: What is the capital of France? -->"
        expected_response = (
            "This is a test.\n"
            '**Asking __perplexity llm__ "What is the capital of France?"**:\n\n'
            "Test response\n"
        )

        result = ask_web_llm(content)
        self.assertEqual(result, expected_response)

        mock_openai.assert_called_once_with(
            api_key="test_api_key", base_url="https://api.perplexity.ai"
        )

        mock_client_instance.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
