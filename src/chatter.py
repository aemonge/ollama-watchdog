"""Here we will define the LLM conversation."""

from typing import AsyncIterator, Awaitable, Callable, cast

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.messages.base import BaseMessageChunk

from src.libs.ask_webllm import ask_web_llm
from src.libs.bash_run import bash_run
from src.libs.file_include import replace_include_tags
from src.libs.http_include import get_website_content
from src.libs.remove_comments import remove_comments
from src.libs.web_search import search_online
from src.models.message_event import MessageEvent
from src.models.subscriber import Subscriber


class Chatter(Subscriber):
    """The main chat interface."""

    def __init__(
        self,
        session_id: str,
        connection_string: str,
        model: str,
        publish_callback: Callable[[MessageEvent], Awaitable[None]],
    ) -> None:
        """
        Construct the LLM chat with SQLite.

        Parameters
        ----------
        session_id : str
            The session ID for the chat.
        connection_string : str
            The connection string for the SQLite database.
        model : str
            The model to use for the LLM.
        publish_callback: Callable[[MessageEvent], Awaitable[None]]
            The callback to publish the event.
        """
        self.model = model
        self.history = SQLChatMessageHistory(
            session_id=session_id, connection_string=connection_string
        )
        self.llm = ChatOllama(model=model)
        self.publish_event = publish_callback

    def _chain_prompt(self, prompt: str) -> str:
        """
        Process the prompt with several chains, and enhancers.

        And then saves it in the DB.

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
        prompt = self._chain_prompt(cast(str, event.contents))
        # self.history.add_user_message(prompt)  # TODO: Make as an event.

        # CREATE AND FIRE THE EVENT
        # self.llm.astream(prompt)

        # self.history.add_ai_message(when_stream_end)  # TODO: Make as an event.

        # Create an instance of the AsyncIterator[BaseMessageChunk] event
        message_chunks: AsyncIterator[BaseMessageChunk] = self.llm.astream(prompt)

        # Publish the new event
        await self.publish_event(
            MessageEvent("messageChunks", "", self.model, message_chunks)
        )
