"""The allow topics and event types."""

from typing import AsyncIterator, Iterator, Literal

from langchain_core.messages.base import BaseMessage, BaseMessageChunk

ExtendedMessage = (
    str
    | BaseMessage
    | BaseMessageChunk
    | Iterator[str | BaseMessage | BaseMessageChunk]
    | AsyncIterator[str | BaseMessage | BaseMessageChunk]
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
