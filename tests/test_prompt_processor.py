import unittest
from unittest.mock import MagicMock, patch

from src.prompt_processor import PromptProcessor


class TestPromptProcessor(unittest.TestCase):
    @patch("src.prompt_processor.remove_comments")
    def test_process_prompt(self, mock_remove_comments):
        """Test that the process_prompt method processes the prompt correctly."""
        mock_publish = MagicMock()
        processor = PromptProcessor(author="Test Author", publish=mock_publish)
        prompt = "Test prompt with <!-- comments -->"
        expected_result = "Test prompt without comments"
        mock_remove_comments.return_value = expected_result

        result = processor.process_prompt(prompt)
        self.assertEqual(result, expected_result)
        mock_remove_comments.assert_called_once_with(prompt)

    @patch("src.prompt_processor.ask_web_llm")
    @patch("src.prompt_processor.bash_run")
    @patch("src.prompt_processor.search_online")
    @patch("src.prompt_processor.replace_include_tags")
    @patch("src.prompt_processor.get_website_content")
    def test_generate_context(
        self,
        mock_get_website_content,
        mock_replace_include_tags,
        mock_search_online,
        mock_bash_run,
        mock_ask_web_llm,
    ):
        """Test that the generate_context method generates context correctly."""
        mock_publish = MagicMock()
        processor = PromptProcessor(author="Test Author", publish=mock_publish)
        prompt = "Test prompt with various processing chains"
        mock_get_website_content.return_value = prompt
        mock_replace_include_tags.return_value = prompt
        mock_search_online.return_value = prompt
        mock_bash_run.return_value = prompt
        mock_ask_web_llm.return_value = prompt

        result = processor.generate_context(prompt)
        self.assertEqual(result, prompt)
        mock_get_website_content.assert_called_once_with(prompt)
        mock_replace_include_tags.assert_called_once_with(prompt)
        mock_search_online.assert_called_once_with(prompt)
        mock_bash_run.assert_called_once_with(prompt)
        mock_ask_web_llm.assert_called_once_with(prompt)


if __name__ == "__main__":
    unittest.main()
