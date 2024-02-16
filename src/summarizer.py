"""The class that will store and summarize the history of conversations."""

import logging
from typing import List, cast

from langchain_core.messages import BaseMessage

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
    ) -> None:
        """
        Summarize with an LLM.

        Parameters
        ----------
        publish : PublisherCallback
            publish a new event to parent
        """
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]

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
        summarization_instructions = BaseMessage(
            type="human",
            content="Distill the above chat messages into a single summary message.\n"
            "Include as many specific details as you can, and avoid adding details.\n"
            "Note that the summary is incremental, so avoid removing key concepts.",
        )
        cast(List[BaseMessage], event.contents).append(summarization_instructions)
        logging.info(event.contents, "debug")

        logging.info('Summarizer is sending a "ask" event')
        event.event_type = "chat_summary"
        await self.publish(["ask"], event)
