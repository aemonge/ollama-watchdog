"""Subscriber abstract class."""

import logging
from abc import abstractmethod
from typing import Any, Callable, Coroutine, List, Optional

from src.models.literals_types_constants import TopicsLiteral
from src.models.message_event import MessageEvent

PublisherCallback = Callable[
    [List[TopicsLiteral], MessageEvent], Coroutine[Any, Any, Optional[MessageEvent]]
]


class PublisherSubscriber:
    """Subscriber abstract class."""

    def is_blocked(self) -> bool:
        """
        Get the value of the block property.

        Returns
        -------
        : bool
            The block value
        """
        logging.critical("Must define the block property")
        return False

    async def block(self, value: bool) -> None:
        """
        Set the value of the block property.

        Parameters
        ----------
        value : bool
            The value to set.
        """
        logging.critical(f"Must define the block method {value}")

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
