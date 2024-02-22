"""Record the conversation between AI and Human in a SQLite DB."""

import logging
from typing import Dict

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages.base import BaseMessage

from src.libs.rich_logger import RichLogging
from src.models.literals_types_constants import SUMMARIZE_EVERY, DatabasePrefixes
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
        self.history: Dict[DatabasePrefixes, SQLChatMessageHistory] = {
            "unprocessed": SQLChatMessageHistory(
                session_id=f"unprocessed-{session_id}",
                connection_string=connection_string,
            ),
            "processed": SQLChatMessageHistory(
                session_id=f"processed-{session_id}",
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

    async def _summarize(self, event: MessageEvent) -> None:
        """
        Trigger the summarize event.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        """
        contents = iter(
            [self._last_human_processed_message, event.contents]
            + self.history["processed"].messages[-SUMMARIZE_EVERY:]
        )
        event = MessageEvent("chat_summary", contents, event.author)

        logging.info('Recorder is sending a "summarize" event')
        logging.debug(event)
        await self.publish(["summarize"], event)

    async def _ai_message(self, event: MessageEvent) -> None:
        """
        Process the AI message.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.

        Returns
        -------
        None
        """
        msg = self._normalize_base_message(event, "ai")
        self.history["processed"].add_message(msg)
        self.history["unprocessed"].add_message(msg)

        if len(self.history["processed"].messages) % SUMMARIZE_EVERY == 0:
            return await self._summarize(event)

        RichLogging.unblock()

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

        contents = iter(self.history["processed"].messages[-SUMMARIZE_EVERY:])
        event = MessageEvent("chat", contents, event.author)

        logging.info('Recorder is sending a "ask" event')
        logging.debug(event)
        await self.publish(["ask"], event)

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
        logging.info('Recorder is sending ["print, "chain"] events')
        logging.debug(event)
        await self.publish(["print", "chain"], event)

    async def _chat_summary(self, event: MessageEvent) -> None:
        """
        Process the chat summary.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        """
        msg = self._normalize_base_message(event, "ai")
        self.history["processed"].add_message(msg)
        RichLogging.unblock()

    async def listen(self, event: MessageEvent) -> None:
        """
        Process the incoming event, specifically looking for chunked responses to store.

        Parameters
        ----------
        event : MessageEvent
            The event containing the chunked response.
        """
        logging.info(f'Recorder listen to "{event.event_type}" event')
        logging.debug(event)
        if event.contents is None:
            logging.error(
                "Cant record empty and None event.contents "
                + f"in {self.__class__.__name__}"
            )

        # Using if / elif instead of match since black complains....
        event_type = event.event_type
        if event_type == "ai_message":
            await self._ai_message(event)

        elif event_type == "chat_summary":
            await self._chat_summary(event)

        elif event_type == "human_processed_message":
            await self._human_processed_message(event)

        elif event_type == "human_raw_message":
            await self._human_raw_message(event)

        else:
            logging.error(f"No event type handler for {event_type=}")
