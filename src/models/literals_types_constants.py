"""The allow topics and event types."""

from typing import AsyncIterator, Dict, List, Literal

from langchain_core.messages.base import BaseMessage, BaseMessageChunk

MessageContentType = (
    str
    | List[str]
    | AsyncIterator[str]
    | BaseMessage
    | List[BaseMessage]
    | AsyncIterator[BaseMessage]
    | BaseMessageChunk
    | List[BaseMessageChunk]
    | AsyncIterator[BaseMessageChunk]
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
    "chat",
    "chat_summary",
    "human_processed_message",
    "human_raw_message",
    "system_message",
]
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
SUMMARIZE_EVERY = 8
VLLM_DOWNLOAD_PATH = "/home/LLM/"

LOG_STYLES: Dict[str, str] = {
    "CRITICAL": "#dc322f bold",
    "ERROR": "#b58900",
    "WARNING": "#268bd2",
    "INFO": "#839496",
    "DEBUG": "#586e75 italic",
}
LOG_LINE_BG = "#002b36"
