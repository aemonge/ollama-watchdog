"""The main twisted PUB/SUB Orchestrate."""

import asyncio

from twisted.internet import asyncioreactor

from src.file_change_event import FileChangeEvent

asyncioreactor.install(asyncio.get_event_loop())

from twisted.internet import reactor

from src.echo import Chatter
from src.watch_dog import Watcher


class PubSubOrchestrator:
    """Manages subscribers and publishes messages."""

    def __init__(self) -> None:
        """Initialize the PubSubOrchestrator."""
        self.subscribers: list[Chatter] = []

    def add_subscriber(self, subscriber: Chatter) -> None:
        """
        Add a subscriber to the orchestrator.

        Parameters
        ----------
        subscriber : Chatter
            The subscriber to add.
        """
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber: Chatter) -> None:
        """
        Remove the subscriber from the orchestrator.

        Parameters
        ----------
        subscriber : Chatter
            The subscriber to remove.
        """
        self.subscribers.remove(subscriber)

    async def publish(self, event: FileChangeEvent) -> None:
        """
        Publish the message to all subscribers.

        Parameters
        ----------
        event : FileChangeEvent
            The event message to publish.
        """
        for subscriber in self.subscribers:
            await subscriber.process_event(event)


async def main_async(orchestrator: PubSubOrchestrator, filename: str) -> None:
    """
    Asynchronously runs the main program.

    Parameters
    ----------
    orchestrator : PubSubOrchestrator
        The orchestrator instance to use for publishing messages.
    filename : str
        The name of the file to watch for modifications.
    """
    loop = asyncio.get_event_loop()
    watcher = Watcher(filename, loop, orchestrator.publish)
    observer = watcher.start_watching()
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        observer.stop()


if __name__ == "__main__":
    orchestrator = PubSubOrchestrator()

    chatter = Chatter(print)
    orchestrator.add_subscriber(chatter)

    filename = "input.md"
    asyncio.ensure_future(main_async(orchestrator, filename))
    reactor.run()
