import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages.base import BaseMessage

from src.models.message_event import MessageEvent, PromptMessage
from src.summarizer import Summarizer


class TestSummarizer(unittest.IsolatedAsyncioTestCase):
    @patch("src.summarizer.PromptTemplate.from_template")
    @patch("src.summarizer.VLLM")
    def test_apply_prompt_template(self, mock_vllm, mock_from_template):
        """Test that the prompt template is applied correctly."""
        mock_publish = MagicMock()
        summarizer = Summarizer(
            publish=mock_publish, llm=mock_vllm, username="test_user"
        )
        mock_template_instance = MagicMock()
        mock_from_template.return_value = mock_template_instance
        mock_template_instance.format.return_value = "Formatted prompt"

        prompt_message = PromptMessage(prompt="Test prompt")
        result = summarizer.apply_prompt_template(prompt_message)
        self.assertEqual(result, "Formatted prompt")
        mock_from_template.assert_called_once()
        mock_template_instance.format.assert_called_once()


if __name__ == "__main__":
    unittest.main()
