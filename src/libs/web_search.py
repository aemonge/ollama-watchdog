"""Searches for a string on the web with search-web."""


import re

from duckduckgo_search import DDGS


def search_online(content: str) -> str:
    """
    Search for a string on Google, amazon, etc...

    Documentation
    -------------
    https://pypi.org/project/search-web/

    Parameters
    ----------
    content: str
        The string to search for on the internet.

    Returns
    -------
    : str
        The results from the search, with markdown response syntax.
        to be used as a next step in the conversation.
    """
    include_pattern = r"(\s*)(<-- *search: (.*?)(?!-->) *-->)(?!-->)"
    content_list = content.split("\n")

    for i, line in enumerate(content_list):
        if match := re.search(include_pattern, line):
            padding = match[1]
            needle = match[3]

            with DDGS() as ddgs:
                results = [
                    f"- [{r.get('title')}]({r.get('href')}). " + f"{r.get('body')}\n"
                    for r in ddgs.text(needle, max_results=7)
                ]

            include_content = results

            # Not add the padding if found
            include_content = [padding + line for line in include_content]

            code_block = [f'{padding}**Web search "{needle}" results**:\n\n']
            code_block += [f"{padding}\n"] + include_content + [f"\n{padding}"]
            content_list[i] = "".join(code_block)

    return "\n".join(content_list)
