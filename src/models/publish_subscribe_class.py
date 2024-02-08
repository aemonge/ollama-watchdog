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
    """Subscriber abstract class."""

    def __init__(self, debug_level: EventsErrorTypes = "debug") -> None:
        """
        Initialize the pub/sub parent class.

        Parameters
        ----------
        debug_level : EventsErrorTypes
            (warning) The type of message to log.
        """
        self._blocked_prompt = False
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
        await self.log("Blocking new messages")

    async def unblock(self) -> None:
        """Allow for new messages."""
        self._blocked_prompt = False
        await self.log("Waiting for new messages")

    @property
    def blocked_prompt(self) -> bool:
        """
        Simple wrapper of the property to get the blocked prompt.

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
        print(DEBUG_LEVELS[message_type])
        _msg = f"DEBUG_LEVELS[message_type]: {DEBUG_LEVELS[message_type]}"
        _msg += "<= DEBUG_LEVELS[cast(EventsErrorTypes, self.debug_level)]: "
        _msg += str(DEBUG_LEVELS[cast(EventsErrorTypes, self.debug_level)])

        await self.publish(
            ["print"], MessageEvent("system_message", "system", _msg, "warning")
        )

        # if (
        #     DEBUG_LEVELS[message_type]
        #     <= DEBUG_LEVELS[cast(EventsErrorTypes, self.debug_level)]
        # ):
        #     await self.publish(
        #         ["print"], MessageEvent("system_message", "system", msg, message_type)
        #     )
        await self.publish(
            ["print"], MessageEvent("system_message", "system", msg, message_type)
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
