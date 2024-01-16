"""Get websites content."""
import re

import requests
from bs4 import BeautifulSoup

from src.constants import TIMEOUT


def get_website_content(content: str) -> str:
    """
    Replace the include tag with http(s) protocol.

    Parameters
    ----------
    content : str
        The content string to process.

    Returns
    -------
    : str
        The content string with the Website content.
    """
    include_pattern = r"(\s*)(<!-- *include: *http(s?)://[^ ]* *-->)"
    include_pattern = r"(\s*)(<!-- *include: *(http(s?)://[^ ]*) *-->)"
    content_list = content.split("\n")

    for i, line in enumerate(content_list):
        if match := re.search(include_pattern, line):
            padding = match[1]
            url = match[3]

            try:
                response = requests.get(url, timeout=TIMEOUT)
                soup = BeautifulSoup(response.text, "html.parser")
                include_content = soup.get_text()

                # Replace double line breaks with a single line break
                include_content = re.sub("\n+", "\n", include_content)

                # Not add the padding if found
                include_content = [padding + line for line in include_content]

            except FileNotFoundError:
                include_content = ["<!-- include website not found -->"]

            code_block = [f"{padding}**{url}**:\n\n"]
            code_block += [f"{padding}```\n"] + include_content + [f"{padding}```"]
            content_list[i] = "".join(code_block)
    return "\n".join(content_list)
