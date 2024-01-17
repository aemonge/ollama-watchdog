#!/usr/bin/env python3

"""Tails a file in markdown rich format."""


import re
import time

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

delimiter = "---"
buffer = ""
console = Console()
in_code_block = False
delimiter_pattern = re.compile(r"\[comment\]: # \(\*\*(.*)\*\* \((.*)\)\)")

with open("output.md", "r") as file:
    while True:
        line = file.readline()
        if not line:
            time.sleep(1)  # sleep for a second before checking for new lines
            continue
        if line.strip() == delimiter:
            line = file.readline()
            if match := delimiter_pattern.match(buffer + line):
                if buffer:
                    md = Markdown(buffer.rstrip("\n"))  # remove trailing newline
                    console.print(md)
                    buffer = ""
                user = Text(match[1], style="bold")
                date = Text(match[2], style="italic")
                title = user + Text(" (") + date + Text(")")
                console.rule(title=title, align="center")
                buffer = ""
            else:
                console.rule()
        elif line.strip().startswith("```"):
            in_code_block = not in_code_block
            buffer += line
        elif (
            in_code_block
            or line.strip().startswith("<")  # noqa: W503
            or line.strip().startswith("|")  # noqa: W503
        ):
            buffer += line
        else:
            buffer += line
            md = Markdown(buffer)  # remove trailing newline
            console.print(md)
            buffer = ""
