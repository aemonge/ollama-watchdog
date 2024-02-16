"""Subscriber abstract class."""

from abc import abstractmethod
from typing import Any, Callable, Coroutine, List, Optional

from src.models.literals_types_constants import TopicsLiteral
from src.models.message_event import MessageEvent

PublisherCallback = Callable[
    [List[TopicsLiteral], MessageEvent], Coroutine[Any, Any, Optional[MessageEvent]]
]


class PublisherSubscriber:
    """Subscriber abstract class."""

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
