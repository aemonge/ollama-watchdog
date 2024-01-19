#!/usr/bin/env python3

# noqa: W503

"""
Tails a file in markdown rich format.

Making sure when a code block if found it will "wait" for it to have it's finishing
tag before printing it. This way the code block is printed out as a whole and Rich
can interpret the MD correctly.

This also prints directly the characters that don't start with special markdown syntax.
Basically we would wait for titles, strong, italic, etc; every other character will be
printed directly.
"""


import os
import re
import time
from io import TextIOWrapper

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

if os.getenv("DEBUG") == "True":
    import debugpy

    debugpy.listen(("127.0.0.1", 5678))
    debugpy.wait_for_client()


class Tail:
    """Tails a file, and applies markdown syntax to it."""

    def __init__(self, file: TextIOWrapper) -> None:
        """
        Initialize the Tails class with regex expressions.

        Parameters
        ----------
        file : TextIOWrapper
            The main file path to tail and process
        """
        self.file = file
        self.console = Console()
        self._buffer = ""

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

        md = Markdown(self._buffer)
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
        code_starts = re.compile(r"^\n```\w*", re.MULTILINE | re.DOTALL)
        code_ends = re.compile(r"```\n$", re.MULTILINE | re.DOTALL)
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

    def tail(self) -> None:
        """Tail and process the file."""
        while True:
            if not (char := file.read(1)):
                time.sleep(3e-2)  # sleep 200 milliseconds
                continue

            if char == "\n":
                if self.is_multiline_block():
                    self.console.print(" ", end="")
                else:
                    self.clear_and_render()
            else:
                self.console.print(char, end="")

            self._buffer += char


with open("output.md", "r") as file:
    tail = Tail(file=file)
    tail.tail()
