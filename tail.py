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

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

buffer = ""
console = Console()
delimiter_pattern = re.compile(r"^---")
author_comment_pattern = re.compile(r"^\[comment\]: # \(\*\*(.*)\*\* \((.*)\)\)")

markdown_line_syntax = re.compile(r"^(\s*[-*+]\s*|\s*\d+\.\s*|#{1,6}\s*|>\s*)")
markdown_blockline = re.compile(r"^\s*(```\w*)")
markdown_blockline_start = re.compile(r"^\s*`$")
markdown_blockline_start = re.compile(r"^\s*`(?![`]{2})")
markdown_blockline_end = re.compile(r"^\s*(```\w*)")

with open("output.md", "r") as file:
    while True:
        if not (char := file.read(1)):
            time.sleep(0.2)  # sleep 200 milliseconds
            continue
        buffer += char

        if markdown_blockline_start.match(buffer):  # Will possibly start a line-block
            continue

        if markdown_blockline.match(buffer):
            while (line := file.readline()) and not markdown_blockline_end.match(line):
                buffer += line
            buffer += line

            md = Markdown(buffer)
            console.print(md)
            buffer = ""

        elif markdown_line_syntax.match(buffer):
            line = file.readline()
            buffer += line

            if delimiter_pattern.match(buffer):
                line = file.readline()

                if match := author_comment_pattern.match(line):
                    user = Text(match[1], style="bold")
                    date = Text(match[2], style="italic")
                    title = user + Text(" (") + date + Text(")")
                    console.rule(title=title)
                    buffer = ""
                else:
                    console.rule()
                    buffer = line
            else:
                md = Markdown(buffer)
                console.print(md)
                buffer = ""
        else:
            console.print(char, end="")
            buffer = ""
