import unittest
from asyncio import get_event_loop
from unittest.mock import AsyncMock, patch

from watchdog.events import FileModifiedEvent

from src.watcher import Watcher


class TestWatcher(unittest.TestCase):
    @patch("src.watcher.Observer")
    def test_on_modified(self, mock_observer):
        """Test that the watcher handles file modification events correctly."""
        _ = mock_observer
        mock_publish = AsyncMock()  # Use AsyncMock for the publish method
        filename = "test_file.txt"
        author = "test_author"
        loop = get_event_loop()

        watcher = Watcher(
            filename=filename,
            author=author,
            loop=loop,
            publish=mock_publish,
            filter_duplicated_content=False,
        )
        mock_event = FileModifiedEvent(filename)

        with patch(
            "builtins.open",
            unittest.mock.mock_open(read_data="new content"),  # type: ignore
        ):
            watcher.on_modified(mock_event)

        # Verify that the publish method was called with the correct event
        mock_publish.assert_called_once()
        args, _ = mock_publish.call_args
        self.assertEqual(args[0], ["print", "chain"])
        # Since mock_publish is an AsyncMock, it's recognized as a coroutine


if __name__ == "__main__":
    unittest.main()
