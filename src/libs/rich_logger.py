"""Use Rick rule to log messages."""

import logging
from typing import Any, List

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from src.models.literals_types_constants import LOG_LINE_BG, LOG_STYLES


class RichLogging(RichHandler):
    """
    A custom logging handler that uses Rich for prettier logging.

    Display logs with styles and background colors as defined in LOG_STYLES and
    LOG_LINE_BG.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Initialize the RichLogging handler.

        Parameters
        ----------
        args : Any
            Positional arguments passed to RichHandler.
        kwargs : Any
            Keyword arguments passed to RichHandler.
        """
        super().__init__(*args, **kwargs)
        self.console = Console()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Process the log record and emits it using Rich's console.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to be emitted.
        """
        for msg in record.getMessage().split("\n"):
            _msg: str = msg if isinstance(msg, str) else repr(msg)

            style: str = LOG_STYLES.get(record.levelname, "")

            parts: List[str] = [
                _msg[i : i + self.console.width]
                for i in range(0, len(_msg), self.console.width)
            ]

            for part in parts:
                self.console.rule(
                    title=Text(part, style=style), align="right", style=LOG_LINE_BG
                )
