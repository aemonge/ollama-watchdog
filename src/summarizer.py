"""The class that will store and summarize the history of conversations."""

from typing import cast

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage
from src.models.literals_types_constants import EventsErrorTypes

from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Summarizer(PublisherSubscriber):
    """The class that will store and summarize the history of conversations."""

    def __init__(
        self,
        model: str,
        publish: PublisherCallback,
        debug_level: EventsErrorTypes = "warning",
    ) -> None:
        """
        Summarize with an LLM.

        Parameters
        ----------
        model : str
            The model to use for the LLM.
        publish : PublisherCallback
            publish a new event to parent
        debug_level : EventsErrorTypes
            The debug level to use.
        """
        super().__init__(debug_level=debug_level)
        self.model = model
        self.llm = ChatOllama(model=model)
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]

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

        await self.log("Summarizing")
        summarization_text = (
            "Distill the above chat messages into a single summary message.\n"
            "Include as many specific details as you can, and avoid adding details.\n"
            # "Note that the summary is incremental, so avoid removing key concepts."
            "Messages:\n\n" + "\n".join([str(message) for message in event.contents])
        )

        await self.log(summarization_text.split("\n"), "debug")
        summary = self.llm.invoke(summarization_text)

        await self.log('Sending a "record" event')
        await self.publish(
            ["record"],
            MessageEvent("chat_summary", self.model, cast(str, summary.content)),
        )
