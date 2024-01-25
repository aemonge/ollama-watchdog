"""
Replaces "include" tags in a given input file.

An include tag is a line of comment that looks like this:
<-- include: file://file.txt -->

This line will be replaced with the contents of the referenced "file.txt" wrapped
in a code block.
"""

import os
import re
from typing import cast


def replace_include_tags(content: str) -> str:
    """
    Replace include tags.

    Parameters
    ----------
    content : str
        The content string to process.

    Returns
    -------
    : str
        The content string with include tags replaced.
    """
    include_pattern = r"(\s*)(<-- *include: file://*[^ ]* *-->)"
    code_marker_ext = {
        "py": "python",
        "js": "javascript",
        "txt": "",
        "html": "html",
        "css": "css",
        "json": "json",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "go": "go",
        "rs": "rust",
        "php": "php",
        "rb": "ruby",
        "swift": "swift",
        "sh": "bash",
        "sql": "sql",
        "yml": "yaml",
        "xml": "xml",
    }

    content_list = content.split("\n")
    for i, line in enumerate(content_list):
        if match := re.search(include_pattern, line):
            padding = match[1]
            include_tag = match[2]
            file_name = cast(
                dict,
                re.search(
                    r"(?P<file_name>^.*?)<--\s*include:\s*file://(?P<path>.*?)\s*-->",
                    include_tag,
                ),
            )["path"]
            include_file = os.path.expanduser(file_name)
            filetype = ""

            try:
                with open(include_file, "r") as f:
                    include_content = f.readlines()

                include_content = [padding + line for line in include_content]

                # Detecting filetype
                extension = include_file.split(".")[-1]
                filetype = code_marker_ext.get(extension, "")
            except FileNotFoundError:
                include_content = ["<-- include file not found -->", "\n"]

            code_block = [f"{padding}**{file_name}**:\n\n"]
            code_block += (
                [f"{padding}```{filetype}\n"] + include_content + [f"{padding}```"]
            )
            content_list[i] = "".join(code_block)

    return "\n".join(content_list)
