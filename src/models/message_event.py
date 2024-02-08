"""Represents a file change event."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.models.literals_types_constants import (
    EventsErrorTypes,
    EventsLiteral,
    EventsLoadingTypes,
    MessageContentType,
)


@dataclass
class MessageEvent:
    """
    Represents a file change event.

    Parameters
    ----------
    event_type : EventsLiteral
        The type of the event.
    author : str
        The author of the event.
    system_type : Optional[EventsErrorTypes | EventsLoadingTypes]
        The system type of event, optional.
    contents : MessageContentType
        The contents of the file.
    created_at : datetime
        The time the event was created.
    """

    event_type: EventsLiteral
    author: Optional[str] = None
    contents: Optional[MessageContentType] = None
    system_type: Optional[EventsErrorTypes | EventsLoadingTypes] = None
    created_at: datetime = field(default_factory=datetime.now)
