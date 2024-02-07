"""Monitors file changes and publishes an event."""

import asyncio
import os
from typing import Optional

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Watcher(FileSystemEventHandler, PublisherSubscriber):
    """Monitors file changes and triggers a event publish."""

    def __init__(
        self,
        filename: str,
        loop: asyncio.AbstractEventLoop,
        publish: PublisherCallback,
        filter_duplicated_content: Optional[bool] = True,
    ) -> None:
        """
        Initialize the Watcher.

        Parameters
        ----------
        filename : str
            The name of the file to watch.
        loop : asyncio.AbstractEventLoop
            The event loop to run asynchronous tasks.
        publish : PublisherCallback
            publish a new event to parent
        filter_duplicated_content : bool, optional
            Whether to filter out events with duplicated content (default is True).
        """
        PublisherSubscriber.__init__(self)  # instead of super()
        FileSystemEventHandler.__init__(self)  # instead of super()
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]
        self.filename: str = filename
        self.loop: asyncio.AbstractEventLoop = loop
        self.filter_duplicated_content = filter_duplicated_content
        self.last_content: Optional[str] = None
        self.user = str(os.getenv("USER"))

    def on_modified(self, event: FileModifiedEvent) -> None:
        """
        Call when a file is modified.

        If filtering is enabled, it checks for content changes before
        triggering the event publish.

        Parameters
        ----------
        event : FileModifiedEvent
            The event object representing the file modification.
        """
        if event.src_path.endswith(self.filename):
            with open(event.src_path, "r") as file:
                current_content = file.read()

            # Check if filtering is enabled and if the content has changed
            if not self.filter_duplicated_content or (
                self.last_content != current_content
            ):
                self.last_content = current_content
                event_data = MessageEvent("human_message", self.user, current_content)
                coroutine = self.publish(["print", "record"], event_data)
                asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    def start_watching(self) -> Observer:  # type: ignore
        """
        Start the observing, and begin watching for file modifications.

        Returns
        -------
        Observer
            The observer instance that is watching the file.
        """
        observer = Observer()
        observer.schedule(self, ".", recursive=False)
        observer.start()
        return observer
