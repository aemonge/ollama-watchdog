"""Represents a file change event."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator, Literal, Optional

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
    """

    event_type: Literal["human_message", "ai_message", "system_message"]
    author: Optional[str] = None
    contents: Optional[str | AsyncIterator[BaseMessageChunk]] = None
    created_at: datetime = field(default_factory=datetime.now)


TopicsLiteral = Literal["record", "print", "chain"]
