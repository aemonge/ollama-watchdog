"""Represents a file change event."""

from dataclasses import dataclass


@dataclass
class FileChangeEvent:
    """
    Represents a file change event.

    Parameters
    ----------
    event_type : str
        The type of the event.
    filename : str
        The name of the file that triggered the event.
    contents : str
        The contents of the file.
    """

    event_type: str
    filename: str
    contents: str
