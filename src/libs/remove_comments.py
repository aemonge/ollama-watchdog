"""Remove comment string from the prompt."""

import re


def remove_comments(content: str) -> str:
    """
    Remove HTML-style comments from Markdown content, including multi-line comments.

    While attempting to preserve original spacing and formatting as closely as possible.
    Perform a triple pass to ensure all comments, surrounding whitespace, and
    formatting are correctly handled.

    Examples
    --------
    >>> remove_comments("inline <!-- ignore me --> comment")
    <<< "inline  comment"
    >>> content = '''This is a test.
    >>> <!-- Start of a multi-line comment
    >>> It continues here
    >>> And ends here -->
    >>> The end of the test.'''
    >>> remove_comments(content)
    <<< This is a test.
    <<< The end of the test.

    Parameters
    ----------
    content : str
        The content string to process.

    Returns
    -------
    : str
        The content without comments
    """
    html_comment_pattern = re.compile(r"<!--.*?-->(\n)?", re.DOTALL)
    return re.sub(html_comment_pattern, "", content).strip()
