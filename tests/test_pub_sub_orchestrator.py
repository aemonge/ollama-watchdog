import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from src.models.message_event import MessageEvent
from src.pub_sub_orchestrator import PubSubOrchestrator


class TestPubSubOrchestrator(unittest.TestCase):
    @patch("src.pub_sub_orchestrator.VLLM")
    @patch("src.pub_sub_orchestrator.RichLogging")
    def test_init(self, mock_rich_logging, mock_vllm):
        """Test that the PubSubOrchestrator initializes correctly."""
        _, _ = mock_rich_logging, mock_vllm
        orchestrator = PubSubOrchestrator(
            prompt_file="test_prompt.txt", model="mock", enable_stream=False
        )
        self.assertEqual(orchestrator.filename, "test_prompt.txt")
        self.assertEqual(orchestrator.model, "mock")
        self.assertFalse(orchestrator.enable_stream)
        self.assertIsNotNone(orchestrator.llm)
        self.assertIsNotNone(orchestrator.printer)
        self.assertIsNotNone(orchestrator.chatter)
        self.assertIsNotNone(orchestrator.prompt_processor)
        self.assertIsNotNone(orchestrator.recorder)
        self.assertIsNotNone(orchestrator.summarizer)
        self.assertIsNotNone(orchestrator.watcher)

    @patch("src.pub_sub_orchestrator.VLLM")
    @patch("src.pub_sub_orchestrator.RichLogging")
    def test_publish(self, mock_rich_logging, mock_vllm):
        """Test that the publish method routes messages correctly."""
        _, _ = mock_rich_logging, mock_vllm
        orchestrator = PubSubOrchestrator(
            prompt_file="test_prompt.txt", model="mock", enable_stream=False
        )
        mock_listener = AsyncMock()
        orchestrator.listeners["ask"] = [mock_listener]
        event = MessageEvent(
            event_type="ai_message", contents="Test content", author="Test Author"
        )

        asyncio.run(orchestrator.publish(["ask"], event))
        mock_listener.listen.assert_called_once_with(event)


if __name__ == "__main__":
    unittest.main()
