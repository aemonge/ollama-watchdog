"""Represents a file change event."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Literal, Optional

from langchain_core.messages.base import BaseMessageChunk


@dataclass
class MessageEvent:
    """
    Represents a file change event.

    Parameters
    ----------
    event_type : Literal["human_message", "ai_message", "system_message"]
        The type of the event.
    author : str
        The author of the event.
    contents : str | AsyncIterator[BaseMessageChunk]
        The contents of the file.
    created_at : datetime
        The time the event was created.
    callback : Optional[Callable[[Any], Any]]
        The callback to be called when the event is finished.
    """

    event_type: Literal["human_message", "ai_message", "system_message"]
    author: str
    contents: str | AsyncIterator[BaseMessageChunk]
    created_at: datetime = field(default_factory=datetime.now)
    callback: Optional[Callable[[Any], Any]] = None
