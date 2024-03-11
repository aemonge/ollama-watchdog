import unittest
from unittest.mock import AsyncMock, patch

from src.chatter import Chatter
from src.models.message_event import PromptMessage


class TestChatter(unittest.TestCase):
    @patch("src.chatter.pathlib.Path.read_text")
    @patch("src.chatter.VLLM")
    def test_init(self, mock_vllm, mock_read_text):
        """Test that the Chatter class initializes correctly."""
        mock_read_text.return_value = "template content"
        mock_publish = AsyncMock()
        username = "test_user"
        enable_stream = False

        chatter = Chatter(
            publish=mock_publish,
            llm=mock_vllm,
            username=username,
            enable_stream=enable_stream,
        )

        self.assertEqual(chatter.username, username)
        self.assertEqual(chatter.enable_stream, enable_stream)
        self.assertEqual(chatter.template_content, "template content")
        self.assertEqual(chatter.userinfo_content, "template content")
        mock_read_text.assert_called()

    @patch("src.chatter.pathlib.Path.read_text")
    @patch("src.chatter.VLLM")
    def test_apply_prompt_template(self, mock_vllm, mock_read_text):
        """Test that the prompt template is applied correctly."""
        # Setup
        mock_read_text.return_value = "template content\n{{query}}\n{{context}}"
        mock_publish = AsyncMock()
        chatter = Chatter(publish=mock_publish, llm=mock_vllm)
        prompt_message = PromptMessage(prompt="test prompt", context="test context")

        # Test
        result = chatter.apply_prompt_template(prompt_message)

        # Assert
        print(result)
        self.assertIn("test prompt", result)
        self.assertIn("test context", result)


if __name__ == "__main__":
    unittest.main()
