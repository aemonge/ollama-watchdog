"""Monitors file changes and triggers a callback."""

import asyncio
import os
from typing import Any, Callable, Optional

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.models.message_event import MessageEvent


class Watcher(FileSystemEventHandler):
    """Monitors file changes and triggers a callback."""

    def __init__(
        self,
        filename: str,
        loop: asyncio.AbstractEventLoop,
        callback: Callable[[MessageEvent], Any],
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
        callback : Callable[[MessageEvent], Any]
            The callback function to be called when a file is modified.
        filter_duplicated_content : bool, optional
            Whether to filter out events with duplicated content (default is True).
        """
        super().__init__()
        self.filename: str = filename
        self.loop: asyncio.AbstractEventLoop = loop
        self.callback: Callable[[MessageEvent], Any] = callback
        self.filter_duplicated_content = filter_duplicated_content
        self.last_content: Optional[str] = None
        self.user = str(os.getenv("USER"))

    def on_modified(self, event: FileModifiedEvent) -> None:
        """
        Call when a file is modified.

        If filtering is enabled, it checks for content changes before
        triggering the callback.

        Parameters
        ----------
        event : FileModifiedEvent
            The event object representing the file modification.
        """
        if event.src_path.endswith(self.filename):
            # Read the contents of the file
            with open(event.src_path, "r") as file:
                current_content = file.read()

            # Check if filtering is enabled and if the content has changed
            if not self.filter_duplicated_content or (
                self.last_content != current_content
            ):
                self.last_content = current_content  # Update the last content
                # Create a dictionary to hold the event data
                event_data = MessageEvent(
                    "fileChanges", event.src_path, self.user, current_content
                )
                # Ensure callback is a coroutine function and schedule it to be run
                coroutine = self.callback(event_data)  # This should now be a coroutine
                asyncio.run_coroutine_threadsafe(coroutine, self.loop)
            # If the content is the same and filtering is enabled, do nothing

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
