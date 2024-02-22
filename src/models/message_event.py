"""Represents a file change event."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.models.literals_types_constants import EventsLiteral, ExtendedMessage


@dataclass
class PromptMessage:
    """
    Represents the prompt message for our template format.

    Parameters
    ----------
    context : str
        The context for the prompt.
    prompt : ExtendedMessage
        The prompt it self.
    examples : List[ExtendedMessage]
        The examples of the prompt
    history : List[ExtendedMessage]
        The history of the prompt.
    """

    prompt: ExtendedMessage
    context: Optional[str] = None
    examples: Optional[List[ExtendedMessage]] = None
    history: Optional[List[ExtendedMessage]] = None
    history_sumarized: Optional[str] = None


@dataclass
class MessageEvent:
    """
    The main message type send through our event system.

    Parameters
    ----------
    event_type : EventsLiteral
        The type of the event.
    contents : MessageContentType
        The contents of the file.
    author : str
        The author of the event.
    created_at : datetime
        The time the event was created.
    """

    event_type: EventsLiteral
    contents: ExtendedMessage | PromptMessage
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
