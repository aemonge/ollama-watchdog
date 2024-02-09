"""The class that will store and summarize the history of conversations."""

import asyncio
from typing import AsyncIterator, List, cast

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.messages.base import BaseMessageChunk

from src.models.literals_types_constants import EventsErrorTypes
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Summarizer(PublisherSubscriber):
    """The class that will store and summarize the history of conversations."""

    def __init__(
        self,
        publish: PublisherCallback,
        model: str = "mock",
    ) -> None:
        """
        Summarize with an LLM.

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

    def _mock_invoke(self) -> BaseMessageChunk:
        """
        Mock of the `invoke` method.

        Returns
        -------
        : BaseMessageChunk
            A mock response encapsulating the summary.
        """
        mock_summary = "This is a mock summary."
        return BaseMessageChunk(type="ai", content=mock_summary)

    async def listen(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        if (
            not event.contents
            or not isinstance(event.contents, list)
            or not isinstance(event.contents[0], BaseMessage)
        ):
            _msg = "Event contents isn't a 'List[BaseMessage]' "
            _msg += f"in {self.__class__.__name__}"
            await self.log(_msg, "error")
            return

        await self.log("Summarizing")
        summarization_instructions = (
            "Distill the above chat messages into a single summary message.\n"
            "Include as many specific details as you can, and avoid adding details.\n"
            # "Note that the summary is incremental, so avoid removing key concepts."
            # "Messages:\n\n" + "\n".join([str(message) for message in event.contents])
        )
        summarization_prompt = cast(List[BaseMessage], event.contents)
        summarization_prompt.append(
            BaseMessage(type="human", content=summarization_instructions)
        )
        await self.log(summarization_prompt, "debug")

        if self.model == "mock":
            summary = self._mock_invoke()
        else:
            summary = self.llm.invoke(summarization_prompt)

        await self.log('Sending a "record" event')
        await self.publish(
            ["record"],
            MessageEvent("chat_summary", self.model, cast(str, summary.content)),
        )
