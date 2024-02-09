"""Subscriber abstract class."""

from abc import abstractmethod
from typing import Any, Callable, Coroutine, List, Optional, cast

from src.models.literals_types_constants import (
    DEBUG_LEVELS,
    EventsErrorTypes,
    MessageContentType,
    TopicsLiteral,
)
from src.models.message_event import MessageEvent

PublisherCallback = Callable[
    [List[TopicsLiteral], MessageEvent], Coroutine[Any, Any, Optional[MessageEvent]]
]


class PublisherSubscriber:
    """Subscriber abstract class.

    Todo
    ----
    -   Need debug_level and block ans singleton properties. # BUG
    """

    def __init__(self, debug_level: EventsErrorTypes = "trace") -> None:
        """
        Initialize the pub/sub parent class.

        Parameters
        ----------
        debug_level : EventsErrorTypes
            (warning) The type of message to log.
        """
        self.debug_level = debug_level

    async def block(self, show_spinner: bool = False) -> None:
        """
        Block new messages waiting for the process.

        Parameters
        ----------
        show_spinner : bool
            (False) Show a spinner while waiting for new messages.
        """
        self._blocked_prompt = True
        await self.log('"Blocking" new messages', "trace")

    async def unblock(self) -> None:
        """Allow for new messages."""
        self._blocked_prompt = False
        await self.log("-" * 20, "trace")
        await self.log("Waiting for new messages", "trace")

    @property
    # @classmethod
    def blocked_prompt(self) -> bool:
        """
        Wrap the property to get the blocked prompt.

        Returns
        -------
        : bool
            The blocked prompt.
        """
        return self._blocked_prompt

    async def log(
        self, msg: MessageContentType, message_type: EventsErrorTypes = "trace"
    ) -> None:
        """
        Use the "print" topic, and "system_message" to log messages.

        Parameters
        ----------
        msg : MessageContentType
            The message to log.
        message_type : EventsErrorTypes
            The type of message to log.
        """
        if (
            DEBUG_LEVELS[message_type]
            <= DEBUG_LEVELS[cast(EventsErrorTypes, self.debug_level)]
        ):
            await self.publish(
                ["print"],
                MessageEvent(
                    event_type="system_message",
                    author="system",
                    contents=msg,
                    system_type=message_type,
                ),
            )

    @abstractmethod
    def listen(
        self, event: MessageEvent  # noqa: U100
    ) -> Coroutine[None, None, Optional[MessageEvent]]:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.

        Returns
        -------
        : Coroutine[None, None, Optional[MessageEvent]]
            The processed event.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @abstractmethod
    async def publish(
        self, /, topics: List[TopicsLiteral], event: MessageEvent  # noqa: U100
    ) -> Optional[MessageEvent]:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        topics: List[TopicsLiteral]
            The topics to subscriber the event from.
        event : MessageEvent
            The event to process.

        Returns
        -------
        : Coroutine[None, None, Optional[MessageEvent]]
            The processed event.
        """
        raise NotImplementedError("Subclasses should implement this method.")
