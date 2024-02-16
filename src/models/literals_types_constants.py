"""The allow topics and event types."""

from typing import Any, AsyncIterator, Coroutine, Iterator, List, Literal

from langchain_core.messages.base import BaseMessage, BaseMessageChunk

MessageContentType = (
    str
    | Coroutine[Any, Any, str]
    | List[str]
    | Iterator[str]
    | AsyncIterator[str]
    | BaseMessage
    | List[BaseMessage]
    | Iterator[BaseMessage]
    | AsyncIterator[BaseMessage]
    | BaseMessageChunk
    | List[BaseMessageChunk]
    | Iterator[BaseMessageChunk]
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
SUMMARIZE_EVERY = 8 * 2
VLLM_DOWNLOAD_PATH = "/home/LLM/"
