"""Here we define the watching file operations, including reading and writing."""

import os
import threading
from pathlib import Path
from time import time
from typing import Any, Callable, Iterator, Optional, cast

from langchain_core.messages.base import BaseMessageChunk
from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.constants import RESPONSE_TIMEOUT


class Watcher:
    """The watcher class and event handles (on_prompt, on_respond)."""

    prompt_file: Path
    conversation_file: Path
    on_prompt: Callable[[Any], None]
    on_respond: Callable[[Any], None]
    last_prompt: str
    prompt_observer: Any  # Observer

    def __init__(
        self,
        prompt_file: Path,
        conversation_file: Path,
        on_prompt: Callable[[Any], None],
        on_respond: Callable[[Any], None],
        create_files: Optional[bool] = True,
    ) -> None:
        """
        Build the watcher class.

        Parameters
        ----------
        prompt_file : Path
            The path to the prompt file.
        conversation_file : Path
            The path to the conversation file.
        on_prompt : Callable[[Any], None]
            The function to call when a prompt is received.
        on_respond : Callable[[Any], None]
            The function to call when a finished response is received.
        create_files : bool, optional
            Whether to create the files if they don't exist.
        """
        self.prompt_file = prompt_file
        self.conversation_file = conversation_file
        self.on_prompt = on_prompt
        self.on_respond = on_respond
        self.last_prompt = ""
        self.prompt_observer = Observer()
        self._prompt_debounce_timer = None
        self._response_debounce_timer = None

        if (not prompt_file.exists()) and create_files:
            open(prompt_file, "w").close()

        if (not conversation_file.exists()) and create_files:
            open(conversation_file, "w").close()

    def start(self) -> None:
        """Start watching the files."""
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = self._on_modified
        self.prompt_observer.schedule(event_handler, self.prompt_file, recursive=False)
        self.prompt_observer.start()

    def _on_modified(self, event: FileSystemEvent) -> None:
        """Call when a file is modified.

        Parameters
        ----------
        event : FileSystemEvent
            The event that was triggered by the watchdog.
        """
        if isinstance(event, FileModifiedEvent):
            with open(event.src_path, "r") as file:
                current_prompt = file.read()

            if current_prompt != self.last_prompt and current_prompt.strip():
                # Use a timer to debounce the on_prompt function
                if self._prompt_debounce_timer is not None:
                    self._prompt_debounce_timer.cancel()

                self._prompt_debounce_timer = threading.Timer(
                    0.25, self.on_prompt, args=(current_prompt,)
                )
                self._prompt_debounce_timer.start()

                self.last_prompt = current_prompt

    def receive_message(
        self, message: str | Iterator[BaseMessageChunk], buffered: bool = True
    ) -> None:
        """
        Receive a message and append it to the conversation file.

        Parameters
        ----------
        message : Union[str, Iterator[BaseMessageChunk]]
            The content to append to the conversation file.
        buffered: bool
            (True) If true, saves the message to avoid duplication
        """
        start_time = time()
        with open(self.conversation_file, "a", os.O_NONBLOCK) as file:
            if isinstance(message, str):
                file.write(message)
                if buffered:
                    self.current_response = message
            else:
                for chunk in message:
                    file.write(cast(str, chunk.content))
                    file.flush()
                    if time() - start_time > RESPONSE_TIMEOUT:
                        break
                file.write("\n")
                self.current_response = "".join(cast(str, x.content) for x in message)

        # Cancel the previous timer if it's still waiting
        if self._response_debounce_timer is not None:
            self._response_debounce_timer.cancel()

        # Create a new timer
        self._response_debounce_timer = threading.Timer(
            0.25, self.on_respond, args=(self.current_response,)
        )
        self._response_debounce_timer.start()
