"""Watches the input file for changes."""

import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler

from src.messages import Messages


class WatcherHandler(FileSystemEventHandler):
    """
    Watches the input directory for changes and copies the file to the output directory.

    Using watchdog to monitor the input directory for changes.
    """

    def __init__(
        self,
        src_file: Path,
        dst_file: Path,
        separators: dict,
        model_name: str = "orca-mini",
    ) -> None:
        """
        Initialize the watcher.

        Parameters
        ----------
        src_file : Path
            The file to watch.
        dst_file : Path
            The file to write to.
        separators : dict
            The separators to use when writing the file.
        model_name : str
            (default: orca-mini) The model name to use when writing the file.
        """
        super()
        self.messages = Messages(
            separators=separators,
            dst_file=dst_file,
            src_file=src_file,
            model_name=model_name,
        )
        self.debounce_timer = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Call when a file is modified.

        Parameters
        ----------
        event : FileSystemEvent
            The event that was triggered by the watchdog.
        """
        if isinstance(event, FileModifiedEvent):
            # Cancel the previous timer if it's still waiting
            if self.debounce_timer is not None:
                self.debounce_timer.cancel()

            # Create a new timer
            self.debounce_timer = threading.Timer(0.25, self._process_file)
            self.debounce_timer.start()

    def _process_file(self) -> None:
        """Process changes in the prompt file to render the response file."""
        self.messages.inlcude_prompt()
        self.messages.include_response()
