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
    result = []
    for line in content:
        _line = line.strip()
        if _line and not re.search(comment_regex, _line):
            result.append(_line)

    return "\n".join(result)
