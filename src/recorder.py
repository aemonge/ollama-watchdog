"""Record the conversation between AI and Human in a SQLite DB."""

import logging
from typing import AsyncIterator, Dict, Iterator, cast

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages.base import BaseMessage

from src.libs.rich_logger import RichLogging
from src.models.literals_types_constants import (
    SUMMARIZE_EVERY,
    DatabasePrefixes,
    ExtendedMessage,
)
from src.models.message_event import MessageEvent, PromptMessage
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
            "summarized": SQLChatMessageHistory(
                session_id=f"summarized-{session_id}",
                connection_string=connection_string,
            ),
        }

    async def _normalize_message(
        self, content: ExtendedMessage, type: str = "human"  # noqa: A002
    ) -> BaseMessage | None:
        """
        Normalize the message to a BaseMessage.

        Parameters
        ----------
        content : ExtendedMessage
            The message it self.
        type : str
            The type of message. Defaults to "human".

        Returns
        -------
        BaseMessage
            The normalized message.
        """
        if isinstance(content, BaseMessage):
            return content

        if isinstance(content, str):
            return BaseMessage(content, type=type)

        if isinstance(content, Iterator):
            return BaseMessage("".join(str(part) for part in content), type=type)

        if isinstance(content, AsyncIterator):
            parts = []
            async for part in content:
                parts.append(str(part))
            return BaseMessage("".join(parts), type=type)
        else:
            logging.error(
                f"{self.__class__.__name__}: Unsupported message type {content=}"
            )

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

    async def _trigger_sumarize(self) -> None:
        """Trigger the event to summarize, with information from DB."""
        if not (last_messages := self.history["processed"].messages[-SUMMARIZE_EVERY:]):
            logging.error(
                f"Empty history, cant summarize: in {self.__class__.__name__}"
            )

        else:
            if not (
                history_sumarized := self.history["summarized"].messages[-1]
            ) or not (summary := cast(str, history_sumarized.content)):
                summary = None

            await self.publish(
                ["summarize"],
                MessageEvent(
                    "chat_summary",
                    PromptMessage(history=last_messages, history_sumarized=summary),
                ),
            )

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
        if isinstance(event.contents, PromptMessage):
            logging.error(
                f'{self.__class__.__name__}: Expected "event.contents"'
                + f'to be a "PromptMessage": {event=}'
            )

        if not (
            msg := await self._normalize_message(
                cast(ExtendedMessage, event.contents), type="ai"
            )
        ):
            return

        self.history["processed"].add_message(msg)
        self.history["unprocessed"].add_message(msg)

        if len(self.history["processed"].messages) % SUMMARIZE_EVERY == 0:
            await self._trigger_sumarize()

        RichLogging.unblock()

    async def _human_processed_message(self, event: MessageEvent) -> None:
        """
        Process the human processed message.

        Parameters
        ----------
        event : MessageEvent
            The event containing the message.
        """
        if (
            not isinstance(event.contents, PromptMessage)
            or not event.contents.prompt
            or not (
                msg := await self._normalize_message(event.contents.prompt, type="ai")
            )
        ):
            return

        if history_sumarized := self.history["summarized"].messages:
            history_sumarized = cast(str, history_sumarized[-1].content)
        else:
            history_sumarized = None

        event = MessageEvent(
            "chat",
            PromptMessage(
                cast(str, msg.content),
                history=self.history["processed"].messages[-SUMMARIZE_EVERY:],
                history_sumarized=history_sumarized,
            ),
            event.author,
        )

        self._last_human_processed_message = msg
        self.history["processed"].add_message(msg)

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
        if msg := await self._normalize_message(
            cast(ExtendedMessage, event.contents), type="ai"
        ):
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
        if msg := await self._normalize_message(
            cast(ExtendedMessage, event.contents), type="ai"
        ):
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
