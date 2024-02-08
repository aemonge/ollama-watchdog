"""Record the conversation between AI and Human in a SQLite DB."""

from typing import Dict, cast

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from src.models.literals_types_constants import DatabasePrefixes, EventsErrorTypes
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
                self.history["processed"].add_ai_message(
                    cast(AIMessage, event.contents)
                )
                self.history["unprocessed"].add_ai_message(
                    cast(AIMessage, event.contents)
                )

                contents = [
                    self._last_human_processed_message,
                    cast(BaseMessage, event.contents)
                ]
                if self.history["summarized"].messages:
                    contents += [self.history["summarized"].messages[-1]]

                await self.log('Sending a "summarize" event')
                await self.publish(["summarize"], MessageEvent(
                    "chat_summary",
                    event.author,
                    contents=contents
                ))

            case "chat_summary":
                self.history["summarized"].add_ai_message(
                    cast(AIMessage, event.contents)
                )
                await self.unblock()

            case "human_processed_message":
                self._last_human_processed_message = event.contents
                self.history["processed"].add_user_message(
                    cast(HumanMessage, event.contents)
                )
                contents = [cast(BaseMessage, event.contents)]
                if self.history["summarized"].messages:
                    contents += [self.history["summarized"].messages[-1]]
                await self.log('Sending "ask" event')
                await self.publish(["ask"], MessageEvent(
                    "chat_summary",
                    event.author,
                    contents=contents
                ))

            case "human_raw_message":
                self.history["unprocessed"].add_user_message(
                    cast(HumanMessage, event.contents)
                )
                await self.log('Sending ["print, "chain"] events')
                await self.publish(["print", "chain"], event)
