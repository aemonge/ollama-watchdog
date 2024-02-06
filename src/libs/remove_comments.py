"""Remove comment string from the prompt."""

import re


def remove_comments(content: str) -> str:
    """
    Remove comment string.

    Todo
    ----
    [ ] Allow inline comment to be processed
        >>> remove_comments("inline <!-- ignore me --> comment")
        <<< "inline commment"

    Parameters
    ----------
    content : str
        The content string to process.

    Returns
    -------
    : str
        The content without comments
    """
    comment_regex = r"<!--(?:.*?)-->"
    content_list = content.split("\n")

    content_filtered = [
        line
        for line in content_list
        if line != "" and not re.search(comment_regex, line)
    ]

    return "\n".join(content_filtered)
