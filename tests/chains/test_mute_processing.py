import unittest
from unittest.mock import MagicMock, patch

from src.chains.mute_processing import MuteProcessing


class TestMuteProcessing(unittest.TestCase):
    @patch("src.chains.mute_processing.RichLogging")
    def test_mute_unmute_processing(self, mock_rich_logging):
        # Mock the context manager returned by RichLogging.quiet()
        mock_context_manager = MagicMock()
        mock_rich_logging.quiet.return_value = mock_context_manager

        mute_processing = MuteProcessing()

        mute_processing.on_llm_start()
        mock_rich_logging.quiet.assert_called_once()
        mock_context_manager.__enter__.assert_called_once()

        mock_context_manager.reset_mock()

        mute_processing.on_llm_end()
        mock_context_manager.__exit__.assert_called_once_with(None, None, None)
