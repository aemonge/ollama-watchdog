"""Here we will define the LLM conversation."""


from langchain_community.chat_models import ChatOllama
from langchain_core.messages.base import BaseMessage

from src.models.literals_types_constants import EventsErrorTypes
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Chatter(PublisherSubscriber):
    """The main chat interface."""

    def __init__(
        self,
        model: str,
        publish: PublisherCallback,
        debug_level: EventsErrorTypes = "warning",
    ) -> None:
        """
        Construct the LLM chat with SQLite.

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

        await self.log(f'Chatting with "{self.model}"')
        await self.log(event.contents, "debug")
        await self.log('Streaming the "print" event')
        await self.publish(
            ["print"],
            MessageEvent(
                "ai_message",
                self.model,
                self.llm.astream(event.contents),
            ),
        )
