"""Watches the input file for changes."""

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler

from src.processor import process


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
        """
        super()
        self.src_file = src_file
        self.dst_file = dst_file
        self.model_name = model_name
        self.separators = separators
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
            self.debounce_timer = threading.Timer(0.25, self.process_file)
            self.debounce_timer.start()

    def process_file(self) -> None:
        """Process the file after a delay."""
        with open(self.src_file, "r") as file:
            file_content = file.read()
            date = datetime.now().strftime("%a, %d %b %H:%M")
            user_prompt = self.separators["pre"].format(
                user=os.getenv("USER"), date=date
            )
            user_prompt += file_content
            user_prompt += self.separators["post"]

        if len(file_content) > 0:
            with open(self.dst_file, "a") as output:
                output.write(user_prompt)

        process_content = process(file_content, model=self.model_name)
        date = datetime.now().strftime("%a, %d %b %H:%M")
        ai_response = self.separators["pre"].format(user=self.model_name, date=date)
        ai_response += process_content
        ai_response += self.separators["post"]

        if len(file_content) > 0:
            with open(self.dst_file, "a") as output:
                output.write(ai_response)
