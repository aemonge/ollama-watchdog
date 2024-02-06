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
[ ] Stop the buffer on <EOF> or <EOB> block end signals
[ ] Fix issue with block code with no language.
"""
import re
from typing import Any, AsyncIterator, Callable, Optional, cast

from langchain_core.messages.base import BaseMessageChunk
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

from src.models.message_event import MessageEvent
from src.models.subscriber import Subscriber


class Printer(Subscriber):
    """Print with beautiful markdown."""

    def __init__(self) -> None:
        """Construct a new Printer."""
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

        self._spin_char_len = len(self.spinner[0]) - 1

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
        if self.is_author_comment():
            pattern = r"\*\*(?P<user>.+?)\*\* \((?P<date>.+?)\)"
            if match := re.search(pattern, self._buffer):
                user = Text(match["user"], style="bold")
                date = Text(match["date"], style="italic")
                title = user + Text(" (") + date + Text(")")
                self.console.rule(title=title)
            self._buffer = ""
            return

        md = Markdown(self._buffer, code_theme="native", justify="left")
        self.console.print(md)
        self._buffer = ""

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

    def is_author_comment(self) -> bool:
        """
        Check if the current buffer is our author comment rule.

        Returns
        -------
        : bool
            If it IS a multi-line block.
        """
        pattern = r'\n{0,1}\[comment\]: # "--- (.*)'
        is_line = re.compile(pattern, re.MULTILINE | re.DOTALL)
        return bool(is_line.search(self._buffer))

    def title(self, event: MessageEvent) -> str:
        """
        Print the title, prettier.

        Parameters
        ----------
        event : MessageEvent
            The message from where to extract the author and date.

        Returns
        -------
        : str
            A pretty title
        """
        title = '[comment]: # "--- (**{author}** ({date}))"'
        date = event.created_at.strftime("%a, %d %b %H:%M - %Y")
        return title.format(author=event.author, date=date) + "\n\n"

    async def pretty_print(
        self,
        text: str | AsyncIterator[BaseMessageChunk],
        callback: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        """
        Process the text.

        Parameters
        ----------
        text : str
            The text to process
        callback: Optional[Callable[[Any], Any]]
            The callback to call when the text is fully processed.

        Raises
        ------
        ValueError
            If the console width is too small.
        """
        column = self.console.width

        if column < 0:
            raise ValueError("Console width is too small.")

        if isinstance(text, str):
            for char in text:
                self._print_char(char, column)
        elif isinstance(text, AsyncIterator):
            full_text = ""
            async for chunk in text:
                for char in chunk.content:
                    full_text += cast(str, char)
                    self._print_char(cast(str, char), column)
            self._print_char("\n", column)
            full_text += "\n"

            if callback is not None:
                callback(full_text)

    def _print_char(self, char: str, column: int) -> None:
        """
        Process the text.

        Parameters
        ----------
        char : str
            The char to process
        column: int
            The column to process
        """
        if char == "\n":
            if self.is_multiline_block():
                self.console.print(" ", end="")
                column -= 1
            else:
                self.clear_and_render()
                column = self.console.width
        elif column > 0:
            self.console.print(char, end="")
            column -= 1
        elif self.spinner is not None:
            self._print_spinner()

        self._buffer += char

    async def process_event(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        if event.author:
            await self.pretty_print(self.title(event))

        await self.pretty_print(event.contents, event.callback)
