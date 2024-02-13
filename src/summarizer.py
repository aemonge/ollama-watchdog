"""The class that will store and summarize the history of conversations."""

import logging
from typing import List, Union, cast

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.base import BaseMessageChunk

from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Summarizer(PublisherSubscriber):
    """
    The class that will store and summarize the history of conversations.

    This are the recommended models for summarization:
    * google/mt5-small
    * DistilBERT
    """

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

    def _convert_base_message(
        self, messages: List[BaseMessage]
    ) -> List[Union[HumanMessage, AIMessage]]:
        """
        Convert the BaseMessage to the correct type.

        @deprecated: As soon as there a fix for the typing issue.

        Parameters
        ----------
        messages : List[BaseMessage]
            The list of BaseMessage to convert.

        Returns
        -------
        : List[Union[HumanMessage, AIMessage]]
            The list of HumanMessage or AIMessage objects.
        """
        _messages = []
        for message in messages:
            if message.type == "human":
                _messages.append(HumanMessage(content=message.content))
            elif message.type == "ai":
                _messages.append(AIMessage(content=message.content))
        return _messages

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
            logging.error(_msg)
            return

        logging.info("Summarizing")
        summarization_instructions = (
            "Distill the above chat messages into a single summary message.\n"
            "Include as many specific details as you can, and avoid adding details.\n"
            "Note that the summary is incremental, so avoid removing key concepts."
        )
        summarization_prompt = cast(List[BaseMessage], event.contents)
        summarization_prompt.append(
            BaseMessage(type="human", content=summarization_instructions)
        )
        logging.info(summarization_prompt, "debug")

        if self.model == "mock":
            summary = self._mock_invoke()
        else:
            summary = self.llm.invoke(
                self._convert_base_message(cast(List[BaseMessage], event.contents))
            )

        logging.info('Sending a "record" event')
        await self.publish(
            ["record"],
            MessageEvent("chat_summary", self.model, cast(str, summary.content)),
        )
