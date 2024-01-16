"""Process the contents of the input query file."""

from libs.file_include import replace_include_tags
from libs.http_include import get_website_content


def process(contents: str) -> str:
    """
    Process the contents of the input query file.

    Parameters
    ----------
    contents : str
        The contents of the input query file.

    Returns
    -------
    : str
        The processed contents of the input query file.
    """
    result = contents
    result = get_website_content(result)
    result = replace_include_tags(result)
    return result
