"""
Pretty print markdown and blocks of markdown.

Making sure when a code block if found it will "wait" for it to have it's finishing
tag before printing it. This way the code block is printed out as a whole and Rich
can interpret the MD correctly.

This also prints directly the characters that don't start with special markdown syntax.
Basically we would wait for titles, strong, italic, etc; every other character will be
printed directly.

Todo
----
[ ] Use the rich spinner...
    https://rich.readthedocs.io/en/latest/reference/spinner.html?highlight=style
[ ] Stop the buffer on <EOF> or <EOB> block end signals
[ ] Fix issue with block code with no language.
"""
import logging
import re
from typing import AsyncGenerator, AsyncIterator, Coroutine, Generator, Iterator

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

from src.models.literals_types_constants import MessageContentType
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Printer(PublisherSubscriber):
    """Print with beautiful markdown."""

    def __init__(self, publish: PublisherCallback) -> None:
        """
        Construct a new Printer.

        Parameters
        ----------
        publish : PublisherCallback
            publish a new event to parent
        """
        self.console = Console()
        self._buffer = ""
        self._spinId = 0
        self.spinner = [
            "     ",
            " •   ",
            " ••  ",
            " ••• ",
            " ••  ",
            " •   ",
            "     ",
            "   • ",
            "  •• ",
            " ••• ",
            "  •• ",
            "   • ",
        ]

        self._column = self.console.width
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]
        self._spin_char_len = len(self.spinner[0])

    def _print_spinner(self) -> None:
        """Print a loading spinner."""
        self._spinId = (self._spinId + 1) % len(self.spinner)
        max_len = self.console.width - self._spin_char_len

        spined_msg = self._buffer[:max_len]
        spined_msg = spined_msg.replace("\n", "")
        spined_msg += self.spinner[self._spinId]

        # Print the new message
        print("\r" + spined_msg, end="\r")  # noqa: T201

    def clear_and_render(self) -> None:
        """Clear the current line and render the pending buffer."""
        if not self._buffer:
            return

        print("\r" + " " * (self.console.width - 1), end="\r")  # noqa: T201
        md = Markdown(self._buffer, code_theme="native", justify="left")
        self.console.print(md)
        self._buffer = ""
        self._column = self.console.width

    def is_multiline_block(self) -> bool:
        """
        Check if current buffer is a markdown multi-line block.

        To render it as a block with Markdown, supporting this blocks

        1. Ordered List
        2. Unordered List
        3. Table (missing)
        4. Code Block

        Returns
        -------
        : bool
            If it IS a multi-line block.
        """
        code_starts = re.compile(r"^\n?```", re.MULTILINE | re.DOTALL)
        code_ends = re.compile(r"```.?$", re.MULTILINE | re.DOTALL)
        if code_starts.search(self._buffer):
            return not code_ends.search(self._buffer)

        if re.compile(r"\n{2}", re.MULTILINE | re.DOTALL).search(self._buffer):
            return False  # Quickly escape if triple \n is found not in code though

        list_starts = re.compile(r"^\n\d+\.\s", re.MULTILINE | re.DOTALL)
        list_ends = re.compile(r"\n^(?!\d+\.\s)$", re.MULTILINE | re.DOTALL)
        if list_starts.search(self._buffer):
            return not list_ends.search(self._buffer)

        ulist_starts = re.compile(r"^\n-\s+", re.MULTILINE | re.DOTALL)
        ulist_ends = re.compile(r"\n^(?!-\s+)$", re.MULTILINE | re.DOTALL)
        if ulist_starts.search(self._buffer):
            return not ulist_ends.search(self._buffer)

        return False

    def title(self, event: MessageEvent) -> None:
        """
        Print the title, prettier.

        Parameters
        ----------
        event : MessageEvent
            The message from where to extract the author and date.
        """
        if event.author is None or event.created_at is None:
            return

        user = Text(event.author, style="bold")
        date = Text(event.created_at.strftime("%a, %d %b %H:%M - %Y"), style="italic")
        title = user + Text(" (") + date + Text(")")
        self.console.rule(title=title)

    async def pretty_print(self, text: MessageContentType) -> None:
        """
        Process the text.

        Parameters
        ----------
        text : MessageContentType
            The text to process

        Raises
        ------
        ValueError
            If the console width is too small.
        """
        self._column = self.console.width

        if self._column < 0:
            raise ValueError("Console width is too small.")

        full_text = ""
        if isinstance(text, str):
            for char in text:
                self._print_char(char)
                full_text += char
        elif isinstance(text, (AsyncIterator, AsyncGenerator)):
            async for chunk in text:
                _content = getattr(chunk, "content", chunk)
                for char in _content:
                    if isinstance(char, str):
                        self._print_char(char)
                        full_text += char
        elif isinstance(text, (Iterator, Generator)):
            for chunk in text:
                _content = getattr(chunk, "content", chunk)
                for char in _content:
                    if isinstance(char, str):
                        self._print_char(char)
                        full_text += char

        full_text += "\n"
        self._print_char("\n")

    def _print_char(self, char: str) -> None:
        """
        Process the text.

        Parameters
        ----------
        char : str
            The char to process
        """
        if char == "\n":
            if self.is_multiline_block():
                self._column -= 1
            else:
                self.clear_and_render()
                self._column = self.console.width
        elif self._column > 0:
            self.console.print(char, end="")
            self._column -= 1
        elif self.spinner is not None:
            self._print_spinner()

        self._buffer += char

    async def listen(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        logging.info(f'Printer listen to "{event.event_type}" event')
        logging.debug(event)
        if event.contents is None or event.author is None:
            logging.error("event.contents is None or event.author is None")
            logging.error(event)
            return

        self.title(event)
        await self.pretty_print(event.contents)
