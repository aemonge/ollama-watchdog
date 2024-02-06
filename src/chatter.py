"""Here we will define the LLM conversation."""

import asyncio
from typing import AsyncIterator, Awaitable, Callable

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.messages.base import BaseMessageChunk

from src.libs.ask_webllm import ask_web_llm
from src.libs.bash_run import bash_run
from src.libs.file_include import replace_include_tags
from src.libs.http_include import get_website_content
from src.libs.remove_comments import remove_comments
from src.libs.web_search import search_online
from src.models.message_event import MessageEvent
from src.models.subscriber import Subscriber


async def mock_astream() -> AsyncIterator[BaseMessageChunk]:
    yield BaseMessageChunk("hello")
    await asyncio.sleep(0.1)  # Simulate some delay
    yield BaseMessageChunk(" | ")
    await asyncio.sleep(0.1)  # Simulate some delay
    yield BaseMessageChunk("world")


class Chatter(Subscriber):
    """The main chat interface."""

    def __init__(
        self,
        model: str,
        publish_callback: Callable[[MessageEvent], Awaitable[None]],
        history: SQLChatMessageHistory,
    ) -> None:
        """
        Construct the LLM chat with SQLite.

        Parameters
        ----------
        model : str
            The model to use for the LLM.
        publish_callback: Callable[[MessageEvent], Awaitable[None]]
            The callback to publish the event.
        history: SQLChatMessageHistory
            The stored messages in the database.
        """
        self.model = model
        self.llm = ChatOllama(model=model)
        self.publish_event = publish_callback
        self.history = history

    def _chain_prompt(self, prompt: str) -> str:
        """
        Process the prompt with several chains, and enhancers.

        And then saves it in the DB.

        Todo
        ----
        [ ] Use me.....

        Parameters
        ----------
        prompt : str
            The raw content from the prompt file.

        Returns
        -------
        : str
            The enhanced and chained prompt
        """
        prompt = remove_comments(prompt)
        prompt = get_website_content(prompt)
        prompt = replace_include_tags(prompt)
        prompt = search_online(prompt)
        prompt = bash_run(prompt)
        prompt = ask_web_llm(prompt)
        return prompt

    async def process_event(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        _ = event
        if not self.history.messages or not isinstance(
            self.history.messages[-1], HumanMessage
        ):
            return

        message_chunks: AsyncIterator[BaseMessageChunk] = self.llm.astream(
            self.history.messages
        )

        await self.publish_event(
            MessageEvent(
                "ai_message",
                self.model,
                message_chunks,
                callback=self.history.add_ai_message,
            )
        )
