"""Subscriber abstract class."""

from abc import abstractmethod
from typing import Any, Callable, Coroutine, List, Optional

from src.logger import Logger
from src.models.literals_types_constants import (
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

    @property
    def block(self) -> bool:
        """
        Get the value of the block property.

        Returns
        -------
        : bool
            The block value
        """
        return Logger.get_instance().block

    @block.setter
    async def block(self, value: bool) -> None:
        """
        Set the value of the block property.

        Parameters
        ----------
        value : bool
            The value to set.
        """
        Logger.get_instance().block = value

    async def log(
        self, msg: MessageContentType, message_type: EventsErrorTypes = "trace"
    ) -> None:
        """
        Use the logger "print" to log messages.

        Parameters
        ----------
        msg : MessageContentType
            The message to log.
        message_type : EventsErrorTypes
            The type of message to log.
        """
        await Logger.get_instance().log(msg, message_type)

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
