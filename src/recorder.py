"""Record the conversation between AI and Human in a SQLite DB."""

import logging
import os
import sqlite3
from pathlib import Path
from typing import AsyncIterator, Iterator, Optional, cast
from uuid import UUID, uuid4

from langchain_core.messages.base import BaseMessage
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from src.libs.rich_logger import RichLogging
from src.models.chat_history import Base as BaseHistory, ChatHistory
from src.models.chat_summary import Base as BaseSummary, ChatSummary
from src.models.literals_types_constants import (
    DB_CONNECTION_STRING,
    DB_PATH,
    SUMMARIZE_EVERY,
    ExtendedMessage,
)
from src.models.message_event import MessageEvent, PromptMessage
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Recorder(PublisherSubscriber):
    """Class to record the conversations."""

    def __init__(
        self,
        publish: PublisherCallback,
        session_id: Optional[UUID] = None,
        conversation_id: Optional[UUID] = None,
    ) -> None:
        """
        Initialize the Recorder.

        Parameters
        ----------
        publish : PublisherCallback
            publish a new event to parent
        session_id : str
            The session ID for the chat.
        conversation_id : str
            The conversation ID for the chat.
        """
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]
        self.session_id = session_id if session_id is not None else uuid4()
        self.conversation_id = (
            conversation_id if conversation_id is not None else uuid4()
        )

        if not Path(DB_PATH).is_file():
            logging.warning(
                f'{self.__class__.__name__}: Creating SQLite file at "{DB_PATH=}"'
            )
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            try:
                sqlite3.connect(DB_PATH).close()
            except sqlite3.Error as e:
                logging.error(
                    f"Failed to create SQLite database file at '{DB_PATH}'. Error: {e}"
                )

        logging.info(
            f"{self.__class__.__name__}: Using the connection string"
            + f' "{DB_CONNECTION_STRING=}"'
        )
        self.engine = create_engine(DB_CONNECTION_STRING)
        BaseSummary.metadata.create_all(self.engine)
        BaseHistory.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

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
        if not (
            history := self.session.query(ChatHistory)
            .order_by(ChatHistory.created_at.desc())
            .limit(SUMMARIZE_EVERY)
            .all()
        ):
            logging.error(
                f'{self.__class__.__name__} did not found any "ChatHistory"'
                + ' to "summarize"'
            )
            return

        event = MessageEvent(
            "chat_summary", PromptMessage(history=history), event.author
        )
        logging.info(f'{self.__class__.__name__} is sending a "summarize" event')
        logging.debug(event)
        await self.publish(["summarize"], event)

    async def _trigger_sumarize(self) -> None:
        """Trigger the event to summarize, with information from DB."""
        if not (
            summary := self.session.query(ChatSummary)
            .order_by(ChatSummary.created_at.desc())
            .first()
        ):
            logging.error(f'{self.__class__.__name__} did not found any "ChatSummary"')
            return

        if not (
            history := self.session.query(ChatHistory)
            .order_by(ChatHistory.created_at.desc())
            .limit(SUMMARIZE_EVERY)
            .all()
        ):
            logging.error(f'{self.__class__.__name__} did not found any "ChatHistory"')
            return

        print(summary)
        print(history)
        event = MessageEvent(
            "chat_summary",
            PromptMessage(history=history, history_sumarized=summary),
        )
        logging.info(f'{self.__class__.__name__} is sending a "summarize" event')
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

        self.session.add(
            ChatHistory(
                session_id=self.session_id,
                conversation_id=self.conversation_id,
                author_name=event.author,
                author_role="ai_message",
                content=msg,
                event_type=event.event_type,
            )
        )
        self.session.commit()
        if (
            count := self.session.query(func.count(ChatHistory.history_id))
            .filter(ChatHistory.session_id == self.session_id)
            .filter(ChatHistory.conversation_id == self.conversation_id)
            .scalar()
        ) and count % SUMMARIZE_EVERY == 0:
            await self._trigger_sumarize()
        else:
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

        history = (
            self.session.query(ChatHistory)
            .order_by(ChatHistory.created_at.desc())
            .limit(SUMMARIZE_EVERY)
            .all()
            or None
        )
        summary = (
            self.session.query(ChatSummary)
            .order_by(ChatSummary.created_at.desc())
            .first()
            or None
        )

        event = MessageEvent(
            "chat",
            PromptMessage(
                cast(str, msg.content), history=history, history_sumarized=summary
            ),
            event.author,
        )

        self.session.add(
            ChatHistory(
                session_id=self.session_id,
                conversation_id=self.conversation_id,
                author_name=event.author,
                author_role="human_message",
                content=msg.content,
                event_type=event.event_type,
            )
        )
        self.session.commit()

        logging.info(f'{self.__class__.__name__} is sending a "ask" event')
        logging.debug(event)
        await self.publish(["ask"], event)

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
            print(msg)
            self.session.add(
                ChatHistory(
                    session_id=self.session_id,
                    conversation_id=self.conversation_id,
                    author_name=event.author,
                    author_role="ai_message",
                    content=msg,
                    event_type=event.event_type,
                )
            )
            self.session.commit()

        RichLogging.unblock()

    async def listen(self, event: MessageEvent) -> None:
        """
        Process the incoming event, specifically looking for chunked responses to store.

        Parameters
        ----------
        event : MessageEvent
            The event containing the chunked response.
        """
        logging.info(f'{self.__class__.__name__} listen to "{event.event_type}" event')
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

        else:
            logging.error(f"No event type handler for {event_type=}")
