"""The allow topics and event types."""

from typing import AsyncIterator, Dict, List, Literal

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    HumanMessage,
    HumanMessageChunk,
)
from langchain_core.messages.base import BaseMessage, BaseMessageChunk

MessageContentType = (
    str
    | List[str]
    | AsyncIterator[BaseMessageChunk]
    | List[BaseMessage]
    | BaseMessage
    | AIMessage
    | AIMessageChunk
    | ChatMessage
    | ChatMessageChunk
    | HumanMessage
    | HumanMessageChunk
)

TopicsLiteral = Literal[
    "ask",
    "chain",
    "print",
    "record",
    "summarize",
    "system",
]
EventsLiteral = Literal[
    "ai_message",
    "chat_summary",
    "human_processed_message",
    "human_raw_message",
    "system_message",
]
EventsErrorTypes = Literal[
    "critical",
    "error",
    "warning",
    "info",
    "trace",
    "debug",
]
DEBUG_LEVELS: Dict[EventsErrorTypes, int] = {
    "critical": 0,
    "error": 1,
    "warning": 2,
    "info": 3,
    "trace": 4,
    "debug": 5,
}
EventsLoadingTypes = Literal[
    "loaded",
    "loading",
]

DatabasePrefixes = Literal[
    "processed",
    "summarized",
    "unprocessed",
]

CONSOLE_PADDING = 1
RESPONSE_TIMEOUT = 10
TIMEOUT = 3000

LOG_STYLES: Dict[EventsErrorTypes, str] = {
    "critical": "red bold",
    "error": "#dc322f",
    "warning": "#b58900",
    "info": "#268bd2",
    "trace": "#839496",
    "debug": "#586e75",
}
LOG_LINE_BG = "#002b36"
