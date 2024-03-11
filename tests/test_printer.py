import unittest
from unittest.mock import MagicMock, patch

from src.models.message_event import MessageEvent
from src.printer import Printer


class TestPrinter(unittest.IsolatedAsyncioTestCase):
    @patch("src.printer.RichLogging")
    def test_init(self, mock_rich_logging):
        """Test that the Printer class initializes correctly."""
        mock_publish = MagicMock()
        printer = Printer(publish=mock_publish)
        self.assertEqual(printer._buffer, "")
        self.assertEqual(printer._spinId, 0)
        self.assertEqual(printer._column, mock_rich_logging.console.width + 1)
        self.assertEqual(printer.publish, mock_publish)

    @patch("src.printer.RichLogging")
    def test_title(self, mock_rich_logging):
        """Test that the title is printed correctly."""
        mock_publish = MagicMock()
        printer = Printer(publish=mock_publish)
        event = MessageEvent(
            event_type="ai_message", contents="Test content", author="Test Author"
        )
        printer.title(event)
        # Verify that console.rule was called with the expected title
        mock_rich_logging.console.rule.assert_called()

    @patch("src.printer.RichLogging")
    async def test_pretty_print(self, mock_rich_logging):
        """Test that pretty_print processes text correctly."""
        mock_rich_logging.console.width = 80
        mock_publish = MagicMock()
        printer = Printer(publish=mock_publish)
        text = "Test message"
        await printer.pretty_print(text)
        # Verify that the console printed the text
        mock_rich_logging.console.print.assert_called()


if __name__ == "__main__":
    unittest.main()
