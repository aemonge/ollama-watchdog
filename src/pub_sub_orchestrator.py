"""Manages subscribers and publishes messages."""

import asyncio
from typing import Dict, List, Optional
from uuid import uuid4

from src.chatter import Chatter
from src.models.message_event import MessageEvent, TopicsLiteral
from src.models.publish_subscribe_class import PublisherSubscriber
from src.printer import Printer
from src.recorder import Recorder
from src.watcher import Watcher


class PubSubOrchestrator:
    """Manages subscribers and publishes messages."""

    def __init__(self, prompt_file: str, model: str) -> None:
        """
        Initialize the PubSubOrchestrator.

        Parameters
        ----------
        prompt_file : str
            The file to watch.
        model : str
            The LLM model to use.
        """
        self.filename = prompt_file

        self.processed_events: set = set()  # Set to store processed event timestamps
        self.subscribers: Dict[TopicsLiteral, list] = {
            "print": [],
            "record": [],
            "chain": [],
        }
        self.printer = Printer(self.publish)
        self.recorder = Recorder(str(uuid4()), "sqlite:///sqlite.db", self.publish)
        self.chatter = Chatter(model, self.publish, self.recorder.history)

        self.add_subscriber("print", self.printer)
        self.add_subscriber("record", self.recorder)
        self.add_subscriber("chain", self.chatter)

    def add_subscriber(
        self, topic: TopicsLiteral, subscriber: PublisherSubscriber
    ) -> None:
        """
        Add a subscriber to the orchestrator.

        Parameters
        ----------
        topic: TopicsLiteral
            The topic to subscriber the event from.
        subscriber : PublisherSubscriber
            The subscriber to add.
        """
        self.subscribers[topic].append(subscriber)

    def remove_subscriber(
        self, topic: TopicsLiteral, subscriber: PublisherSubscriber
    ) -> None:
        """
        Remove the subscriber from the orchestrator.

        Parameters
        ----------
        topic: TopicsLiteral
            The topic to subscriber the event from.
        subscriber : PublisherSubscriber
            The subscriber to remove.
        """
        self.subscribers[topic].remove(subscriber)

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
                for subscriber in self.subscribers[topic]:
                    await subscriber.process_event(event)
                self.processed_events.add(event_id)  # Mark event as processed

    async def start(self) -> None:
        """Asynchronously runs the main program."""
        loop = asyncio.get_event_loop()
        self.watcher = Watcher(self.filename, loop, self.publish)
        observer = self.watcher.start_watching()

        try:
            while True:
                await asyncio.sleep(3600)
        finally:
            observer.stop()
