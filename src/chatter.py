"""Here we will define the LLM conversation."""


import asyncio
from typing import AsyncIterator

from langchain_community.chat_models import ChatOllama
from langchain_core.messages.base import BaseMessage, BaseMessageChunk

from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Chatter(PublisherSubscriber):
    """The main chat interface."""

    def __init__(
        self,
        publish: PublisherCallback,
        model: str = "mock",
    ) -> None:
        """
        Construct the LLM chat with SQLite.

        Parameters
        ----------
        model : str
            The model to use for the LLM.
        publish : PublisherCallback
            publish a new event to parent
        """
        self.model = model
        self.llm = ChatOllama(model=model)
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]

    async def _mock_astream(self) -> AsyncIterator[BaseMessageChunk]:
        """
        Mock of the `astream` method, with "hola mundo.".

        Yields
        ------
        AsyncIterator[BaseMessageChunk]
            An asynchronous iterator of BaseMessageChunk objects.
        """
        await asyncio.sleep(0.3)
        yield BaseMessageChunk(type="ai", content="hola ")
        await asyncio.sleep(0.3)
        yield BaseMessageChunk(type="ai", content="mundo")
        await asyncio.sleep(0.3)
        yield BaseMessageChunk(type="ai", content=".")

    async def listen(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        if not isinstance(event.contents, list) or not isinstance(
            event.contents[0], (str, BaseMessage)
        ):
            msg = f'Type "List[BaseMessage|str]" in {self.__class__.__name__} '
            msg += f"expected: {event.contents}"
            await self.log(msg, "error")
            return

        await self.log(f'Chatting with "{self.model}"')
        if self.model == "mock":
            stream = self._mock_astream()
        else:
            stream = self.llm.astream(event.contents)

        await self.log('Streaming the "print" event')
        await self.publish(
            ["print"],
            MessageEvent("ai_message", self.model, contents=stream),
        )
