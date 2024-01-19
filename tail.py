#!/usr/bin/env python3

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
        self._pennding = ""

        self.delimiter_pattern = re.compile(r"^---")
        self.author_comment_pattern = re.compile(
            r"^\[comment\]: # (\*\*(.*)\*\* \((.*)\))"
        )
        self.author_comment_pattern = re.compile(
            r"^\[comment\]:\s*#\s*\(\*\*(\w+)\*\*\s*\((.*)\)\)"
        )

        # r"^(\s*[-*+]\s*|\s*\d+\.\s*|#{1,6}\s*|>\s*|\[\w*\]\:)"
        # r"^(\s*[-*+]\s*|\s*\d+\.\s*|>\s*|\[\w*\]\:|\#{1,6}|\s*(!?)\[)"
        # r"^(\s*[-*+]\s*|\s*\d+\.\s*|>\s*|\[\w*\]\:)"
        # r"^(#{1,6}\s*|>\s*|\[\w*\]\:)"
        self.re_line_start = re.compile(
            r"^(\s{0,3}[-*+]\s{0,3}|\s{0,3}\d+\.\s{0,3}|>\s{0,3}|\[\w*\]\:|\#{1,6}|\s{4})"
        )

        self.re_undetermined = re.compile(r"^\s{1,3}$")

        self.re_multiline_start = re.compile(r"^\s*`(?![`]{2})$")
        self.re_multiline_end = re.compile(r"^\s*```$")

        self.re_word_start = re.compile(r"^(`|\*{1,2}|\_{1,2}|\[|\(|~{1,2}|==)")
        self.re_word2 = re.compile(
            r"^(`|\*{2}|\_{2}|\[|\(|~{2}|==)[^`\*\_\]\)\~]+(`|\*{2}|\_{2}|\]|\)|~{2}|==)$"
        )
        self.re_word1 = re.compile(
            r"^(`|\*{1}|\_{1}|\[|\(|~{1}|==)[^`\*\_\]\)\~]+(`|\*{1}|\_{1}|\]|\)|~{1}|==)$"
        )

    def _multiline_processor(self, buffer: str) -> None:
        """
        Process the full line in markdown.

        Parameters
        ----------
        buffer : str
            The current character(s) buffer to check for.
        """
        while (line := self.file.readline()) and not (
            self.re_multiline_end.match(line)
        ):
            buffer += line
        buffer += line

        md = Markdown(buffer)
        self.console.print(md)

    def _line_processor(self, buffer: str) -> None:
        """
        Process the full line in markdown.

        Parameters
        ----------
        buffer : str
            The current character(s) buffer to check for.
        """
        line = self.file.readline()
        md = Markdown(buffer + line)
        self.console.print(md)

    def _word_processor(self, buffer: str) -> None:
        """
        Process the full word-block in markdown.

        Parameters
        ----------
        buffer : str
            The current character(s) buffer to check for.
        """
        while (char := self.file.read(1)) and not (
            self.re_word2.match(buffer) or self.re_word1.match(buffer)
        ):
            buffer += char
        buffer += char

        self._pennding += buffer
        print(buffer, end="")  # noqa: T201

    def is_multilineblock(self, buffer: str) -> bool:
        """
        Check if a multi-line-block is potentially starting.

        Parameters
        ----------
        buffer : str
            The current character(s) buffer to check for.

        Returns
        -------
        : bool
            True if the start of the buffer is the start of a multi-line-block
            in markdown
        """
        return bool(self.re_multiline_start.match(buffer))

    def is_lineblock(self, buffer: str) -> bool:
        """
        Check if a line-block is potentially starting.

        Parameters
        ----------
        buffer : str
            The current character(s) buffer to check for.

        Returns
        -------
        : bool
            True if the start of the buffer is the start of a line-block in markdown
        """
        return bool(self.re_line_start.match(buffer))

    def is_wordblock(self, buffer: str) -> bool:
        """
        Check if a word-block is potentially starting.

        Parameters
        ----------
        buffer : str
            The current character(s) buffer to check for.

        Returns
        -------
        : bool
            True if the start of the buffer is the start of a word-block in markdown
        """
        return bool(self.re_word_start.match(buffer))

    def clear_and_render(self) -> None:
        """Clear the current line and render the pending buffer."""
        print("\r" + " " * (self.console.width - 1), end="\r")  # noqa: T201
        md = Markdown(self._pennding)
        self.console.print(md, end="")
        self._pennding = ""

    def tail(self) -> None:
        """Tail and process the file."""
        buffer = ""
        new_line = False
        while True:
            time.sleep(5e-2)  # sleep 200 milliseconds
            if not (char := file.read(1)):
                time.sleep(5e-2)  # sleep 200 milliseconds
                continue
            buffer += char

            if new_line and self.re_undetermined.match(buffer):
                continue

            # if self.is_multilineblock(buffer=buffer):
            #     self._multiline_processor(buffer=buffer)
            #     new_line = True

            # elif self.is_lineblock(buffer=buffer):
            #     self._line_processor(buffer=buffer)
            #     new_line = True

            elif self.is_wordblock(buffer=buffer):
                new_line = False
                self._word_processor(buffer=buffer)

            elif char == "\n":
                self.clear_and_render()
                new_line = True
            else:
                self.console.print(buffer, end="")
                # print(buffer, end="")
                self._pennding += buffer
                new_line = False

            buffer = ""


with open("output.md", "r") as file:
    tail = Tail(file=file)
    tail.tail()
    # while True:
    #     if not (char := file.read(1)):
    #         time.sleep(0.2)  # sleep 200 milliseconds
    #         continue
    #     buffer += char
    #
    #     if markdown_blockline_start.match(buffer):  # Will possibly start a line-block
    #         continue
    #
    #     # if markdown_blockline.match(buffer):
    #     #     while (line := file.readline()) and not markdown_blockline_end.match(line):
    #     #         buffer += line
    #     #     buffer += line
    #     #
    #     #     md = Markdown(buffer)
    #     # console.print(md)
    #
    #     if markdown_line_syntax.match(buffer):
    #         # elif markdown_line_syntax.match(buffer):
    #         line = file.readline()
    #         buffer += line
    #
    #         if delimiter_pattern.match(line) or author_comment_pattern.match(line):
    #             next_line = file.readline()
    #             if next_line.strip() == "":
    #                 next_line = file.readline()
    #
    #             if match := author_comment_pattern.match(next_line):
    #                 user = Text(match[1], style="bold")
    #                 date = Text(match[2], style="italic")
    #                 title = user + Text(" (") + date + Text(")")
    #                 console.rule(title=title)
    #             else:
    #                 console.rule()
    #                 md = Markdown(next_line)
    #                 # console.print(md)
    #             continue
    #         else:
    #             md = Markdown(buffer)
    #             # console.print(md)  # CAPTURES ALL
    #     # else:
    #     #     console.print(char, end="")
    #
    #     buffer = ""
