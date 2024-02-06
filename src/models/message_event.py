"""Represents a file change event."""

from dataclasses import dataclass
from typing import AsyncIterator

from langchain_core.messages.base import BaseMessageChunk


@dataclass
class MessageEvent:
    """
    Represents a file change event.

    Parameters
    ----------
    event_type : str
        The type of the event.
    filename : str
        The name of the file that triggered the event.
    author : str
        The author of the event.
    contents : str | AsyncIterator[BaseMessageChunk]
        The contents of the file.
    """

    event_type: str
    filename: str
    author: str
    contents: str | AsyncIterator[BaseMessageChunk]
