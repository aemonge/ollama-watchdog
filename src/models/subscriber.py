"""Subscriber abstract class."""

from abc import abstractmethod
from typing import Coroutine, Optional

from src.models.message_event import MessageEvent


class Subscriber:
    """Subscriber abstract class."""

    @abstractmethod
    def process_event(
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
