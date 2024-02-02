"""
Tails a file in markdown rich format.

Making sure when a code block if found it will "wait" for it to have it's finishing
tag before printing it. This way the code block is printed out as a whole and Rich
can interpret the MD correctly.

This also prints directly the characters that don't start with special markdown syntax.
Basically we would wait for titles, strong, italic, etc; every other character will be
printed directly.
"""


import re
import time
from io import TextIOWrapper
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text


class Tail:
    """Tails a file, and applies markdown syntax to it."""

    def __init__(self, file: Path) -> None:
        """
        Initialize the Tails class with regex expressions.

        Parameters
        ----------
        file : Path
            The main file path to tail and process
        """
        self.file = file
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
        code_starts = re.compile(r"^\n?```\w*", re.MULTILINE | re.DOTALL)
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

    def _tail(self, file: TextIOWrapper) -> None:
        """
        Tail and process the file.

        Parameters
        ----------
        file : TextIOWrapper
            The buffer file to tail

        Raises
        ------
        ValueError
            If the console width is too small.
        """
        column = self.console.width

        if column < 0:
            raise ValueError("Console width is too small.")

        while True:
            if not (char := file.read(1)):
                time.sleep(3e-2)  # sleep 200 milliseconds
                continue

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

    def start(self) -> None:
        """Start tailing the file."""
        with open(self.file, "r") as file:
            self._tail(file=file)
