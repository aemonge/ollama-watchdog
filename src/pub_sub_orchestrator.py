"""Manages subscribers and publishes messages."""

import asyncio
from uuid import uuid4

from src.chatter import Chatter
from src.models.message_event import MessageEvent
from src.models.subscriber import Subscriber
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
        self.subscribers: list = []
        self.printer = Printer()
        self.recorder = Recorder(str(uuid4()), "sqlite:///sqlite.db")
        self.chatter = Chatter(model, self.publish, self.recorder.history)

        self.add_subscriber(self.printer)
        self.add_subscriber(self.recorder)
        self.add_subscriber(self.chatter)

    def add_subscriber(self, subscriber: Subscriber) -> None:
        """
        Add a subscriber to the orchestrator.

        Parameters
        ----------
        subscriber : Subscriber
            The subscriber to add.
        """
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber: Subscriber) -> None:
        """
        Remove the subscriber from the orchestrator.

        Parameters
        ----------
        subscriber : Subscriber
            The subscriber to remove.
        """
        self.subscribers.remove(subscriber)

    async def publish(self, event: MessageEvent) -> None:
        """
        Publish the message to all subscribers.

        Parameters
        ----------
        event : MessageEvent
            The event message to publish.
        """
        for subscriber in self.subscribers:
            await subscriber.process_event(event)
        # Convert event.created_at to a comparable format if necessary, e.g., timestamp
        event_timestamp = event.created_at.timestamp()
        if event_timestamp not in self.processed_events:
            for subscriber in self.subscribers:
                await subscriber.process_event(event)
            self.processed_events.add(event_timestamp)  # Mark event as processed

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
