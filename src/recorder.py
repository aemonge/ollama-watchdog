"""Record the conversation between AI and Human in a SQLite DB."""

from typing import Dict, cast

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages.base import BaseMessage

from src.models.literals_types_constants import (
    DatabasePrefixes,
    EventsErrorTypes,
    MessageContentType,
)
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Recorder(PublisherSubscriber):
    """Class to record the conversations."""

    def __init__(
        self,
        session_id: str,
        connection_string: str,
        publish: PublisherCallback,
        debug_level: EventsErrorTypes = "warning",
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
        debug_level : EventsErrorTypes
            The debug level to use.
        """
        super().__init__(debug_level=debug_level)
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]
        self.history: Dict[DatabasePrefixes, SQLChatMessageHistory] = {
            "unprocessed": SQLChatMessageHistory(
                session_id=f"unprocessed-{session_id}",
                connection_string=connection_string,
            ),
            "processed": SQLChatMessageHistory(
                session_id=f"processed-{session_id}",
                connection_string=connection_string,
            ),
            "summarized": SQLChatMessageHistory(
                session_id=f"summarized-{session_id}",
                connection_string=connection_string,
            ),
        }

    def _normalize_base_message(
        self, event: MessageEvent, msg_type: str = "human"
    ) -> BaseMessage:
        """
        Normalize the message to a BaseMessage.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        msg_type : str
            The type of message. Defaults to "human".

        Returns
        -------
        BaseMessage
            The normalized message.
        """
        msg = event.contents
        if not isinstance(msg, BaseMessage):
            return BaseMessage(type=msg_type, content=str(msg))
        return msg

    async def _ai_message(self, event: MessageEvent) -> None:
        """
        Process the AI message.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        """
        msg = self._normalize_base_message(event, "ai")
        self.history["processed"].add_message(msg)
        self.history["unprocessed"].add_message(msg)

        contents: MessageContentType = [self._last_human_processed_message, msg]
        if self.history["summarized"].messages:
            contents += self.history["summarized"].messages[-1:]

        await self.log('Sending a "summarize" event')
        await self.publish(["summarize"], MessageEvent(
            "chat_summary",
            event.author,
            contents=contents
        ))

    async def _human_processed_message(self, event: MessageEvent) -> None:
        """
        Process the human processed message.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        """
        msg = self._normalize_base_message(event)

        self._last_human_processed_message = msg
        self.history["processed"].add_message(msg)

        contents: MessageContentType = [msg]
        if self.history["summarized"].messages:
            contents += self.history["summarized"].messages[-1:]

        await self.log('Sending "ask" event')
        await self.publish(["ask"], MessageEvent(
            "chat",
            event.author,
            contents=contents
        ))

    async def _human_raw_message(self, event: MessageEvent) -> None:
        """
        Process the human raw message.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        """
        msg = self._normalize_base_message(event)

        self.history["unprocessed"].add_message(msg)
        await self.log('Sending ["print, "chain"] events')
        await self.publish(["print", "chain"], event)

    async def _chat_summary(self, event: MessageEvent) -> None:
        """
        Process the chat summary.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        """
        self.history["summarized"].add_message(cast(BaseMessage, event.contents))
        await self.unblock()

    async def listen(self, event: MessageEvent) -> None:
        """
        Process the incoming event, specifically looking for chunked responses to store.

        Todo
        ----
        - Use last_message from `SQLChatMessageHistory`, when available.

        Parameters
        ----------
        event : MessageEvent
            The event containing the chunked response.
        """
        await self.log(f'Recording a "{event.event_type}"')
        if event.contents is None:
            await self.log(
                "Cant record empty and None event.contents in {}" + str(
                    self.__class__.__name__
                ),
                "error",
            )
        await self.log(str(event.contents), "debug")

        match event.event_type:
            case "ai_message":
                await self._ai_message(event)
            case "chat_summary":
                await self._chat_summary(event)
            case "human_processed_message":
                await self._human_processed_message(event)
            case "human_raw_message":
                await self._human_raw_message(event)
