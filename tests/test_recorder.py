import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages.base import BaseMessage

from src.models.message_event import MessageEvent
from src.recorder import Recorder


class TestRecorder(unittest.IsolatedAsyncioTestCase):
    @patch("src.recorder.RichLogging")
    @patch("src.recorder.create_engine")
    @patch("src.recorder.sessionmaker")
    async def test_ai_message(
        self, mock_sessionmaker, mock_create_engine, mock_rich_logging
    ):
        _, _ = mock_create_engine, mock_rich_logging
        mock_session = MagicMock()
        mock_sessionmaker.return_value = MagicMock(return_value=mock_session)

        mock_publish = AsyncMock()
        recorder = Recorder(publish=mock_publish)

        prompt_message = BaseMessage("Test AI message", type="ai")
        test_event = MessageEvent(
            event_type="ai_message", contents=prompt_message, author="AI"
        )

        await recorder.listen(test_event)
        mock_session.add.assert_called()


if __name__ == "__main__":
    unittest.main()
