"""Singleton class logger."""

import logging
from typing import Any, Callable, cast

from src.models.literals_types_constants import (
    MessageContentType,
)
from src.models.message_event import MessageEvent


class Logger(object):
    """Singleton class logger."""

    _instance = None

    def __new__(
        cls,
        system_message: Callable[[MessageEvent], Any],
        debug_level: EventsErrorTypes = "warning",
    ) -> "Logger":
        """
        Ensure only one instance of Logger is created (Singleton pattern).

        Parameters
        ----------
        system_message : Callable
            The Callable object to print the system messages.
        debug_level : EventsErrorTypes
            The debug level to use.

        Returns
        -------
        Logger
            The singleton instance of the Logger class.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.system_message = system_message
            cls._instance.debug_level = debug_level
        return cls._instance

    @classmethod
    def get_instance(cls) -> "Logger":  # noqa: ANN102
        """
        Retrieve the singleton instance of the Logger class.

        Returns
        -------
        Logger
            The singleton instance of the Logger class.
        """
        if cls._instance is None:
            cls._instance = cls()  # pyright: ignore
        return cls._instance

    def __init__(
        self,
        system_message: Callable[[MessageEvent], Any],
        debug_level: EventsErrorTypes = "warning",
    ) -> None:
        """
        Initialize the PubSubOrchestrator.

        Parameters
        ----------
        debug_level : EventsErrorTypes
            The debug level to use.
        system_message : Callable[[MessageEvent], Any]
            The Callable object to print the system messages.
        """
        self.system_message = system_message
        self.debug_level = debug_level
        self._block = False

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
            self.system_message(
                MessageEvent(
                    event_type="system_message",
                    author="system",
                    contents=msg,
                    system_type=message_type,
                )
            )

    def is_blocked(self) -> bool:
        """
        Get the value of the block property.

        Returns
        -------
        : bool
            The block value
        """
        return self._block

    async def block(self, value: bool) -> None:
        """
        Set the value of the block property.

        Parameters
        ----------
        value : bool
            The value to set.
        """
        if value:
            logging.debug('"Blocking" new messages', "trace")
        else:
            logging.debug("Waiting for new messages", "trace")

        self._block = value
