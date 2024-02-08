"""Manages subscribers and publishes messages."""

import asyncio
import os
from typing import Dict, List, Optional
from uuid import uuid4

from src.chatter import Chatter
from src.models.literals_types_constants import EventsErrorTypes, TopicsLiteral
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherSubscriber
from src.printer import Printer
from src.prompt_processor import PromptProcessor
from src.recorder import Recorder
from src.summarizer import Summarizer
from src.watcher import Watcher


class PubSubOrchestrator:
    """Manages subscribers and publishes messages."""

    def __init__(
        self, prompt_file: str, model: str, debug_level: EventsErrorTypes
    ) -> None:
        """
        Initialize the PubSubOrchestrator.

        Parameters
        ----------
        prompt_file : str
            The file to watch.
        model : str
            The LLM model to use.
        debug_level : EventsErrorTypes
            The debug level to use.
        """
        self.filename = prompt_file
        self.user = str(os.getenv("USER"))

        self.chatter = Chatter(model, self.publish, debug_level=debug_level)
        self.prompt_processor = PromptProcessor(
            self.user, self.publish, debug_level=debug_level
        )
        self.printer = Printer(self.publish, debug_level=debug_level)
        self.recorder = Recorder(
            str(uuid4()), "sqlite:///sqlite.db", self.publish, debug_level=debug_level
        )
        self.summarizer = Summarizer(model, self.publish, debug_level=debug_level)
        self.watcher = Watcher(
            self.filename,
            self.user,
            asyncio.get_event_loop(),
            self.publish,
            debug_level=debug_level,
        )

        self.processed_events: set = set()  # Set to store processed event timestamps
        self.listeners: Dict[TopicsLiteral, list] = {
            "ask": [self.chatter],
            "chain": [self.prompt_processor],
            "print": [self.printer],
            "record": [self.recorder],
            "summarize": [self.summarizer],
        }

    def listen(
        self, topic: TopicsLiteral, subscribers: List[PublisherSubscriber]
    ) -> None:
        """
        Add a subscriber to the orchestrator.

        Parameters
        ----------
        topic: TopicsLiteral
            The topic to subscriber the event from.
        subscribers : List[PublisherSubscriber]
            The subscribers to add.
        """
        for subscriber in subscribers:
            self.listeners[topic].append(subscriber)

    async def publish(
        self, topics: List[TopicsLiteral], event: MessageEvent  # noqa: U100
    ) -> Optional[MessageEvent]:
        """
        Publish the message to all subscribers.

        Parameters
        ----------
        topics: List[TopicsLiteral]
            The topics to subscriber the event from.
        event : MessageEvent
            The event message to publish.
        """
        for topic in topics:
            event_id = f"{topic}-{event.created_at.timestamp()}"
            if event_id not in self.processed_events:
                for subscriber in self.listeners[topic]:
                    await subscriber.listen(event)
                self.processed_events.add(event_id)  # Mark event as processed

    async def start(self) -> None:
        """Asynchronously runs the main program."""
        observer = self.watcher.start_watching()

        try:
            while True:
                await asyncio.sleep(3600)
        finally:
            observer.stop()
