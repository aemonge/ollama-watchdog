"""Record the conversation between AI and Human in a SQLite DB."""

from typing import cast

from langchain_community.chat_message_histories import SQLChatMessageHistory

from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Recorder(PublisherSubscriber):
    """Class to record the conversations."""

    def __init__(
        self,
        session_id: str,
        connection_string: str,
        publish: PublisherCallback,
    ) -> None:
        """
        Initialize the Recorder.

        Parameters
        ----------
        session_id : str
            The session ID for the chat.
        connection_string : str
            The connection string for the SQLite database.
        publish : PublisherCallback
            publish a new event to parent
        """
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]
        self.history = SQLChatMessageHistory(
            session_id=session_id, connection_string=connection_string
        )

    async def process_event(self, event: MessageEvent) -> None:
        """
        Process the incoming event, specifically looking for chunked responses to store.

        Parameters
        ----------
        event : MessageEvent
            The event containing the chunked response.
        """
        if event.event_type == "human_message":
            self.history.add_user_message(cast(str, event.contents))
            await self.publish(["chain"], MessageEvent("system_message"))
        elif event.event_type == "ai_message":
            self.history.add_ai_message(cast(str, event.contents))
