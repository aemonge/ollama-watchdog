"""Use Rick rule to log messages."""

import logging
import os
import sys
from contextlib import contextmanager
from typing import Any, ClassVar, Iterator, List

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text


class RichLogging(RichHandler):
    """
    A custom logging handler that uses Rich for prettier logging.

    Display logs with styles and background colors as defined in LOG_STYLES and
    LOG_LINE_BG.
    """

    quiet_mode_enabled = False  # Class-level attribute to control quiet mode

    _blocked = True  # Class-level attribute to control quiet mode

    console = Console()

    TRACE_LEVEL_NUM: ClassVar[int] = 15

    LOG_STYLES: ClassVar[dict[str, str]] = {
        "CRITICAL": "#D32F2C bold",
        "ERROR": "#dc322f",
        "WARNING": "#694E00",
        "INFO": "#326990",
        "TRACE": "#586e75",
        "DEBUG": "#38464B",
    }
    LOG_LINE_BG = "#002b36"

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

            style: str = self.LOG_STYLES.get(record.levelname, "")

            parts: List[str] = [
                _msg[i : i + self.console.width]
                for i in range(0, len(_msg), self.console.width)
            ]

            for part in parts:
                self.console.rule(
                    title=Text(part, style=style), align="right", style=self.LOG_LINE_BG
                )

    @classmethod
    def block(cls) -> None:
        """Set block to True."""
        logging.info("Blocking the input read.")
        cls._blocked = True

    @classmethod
    def unblock(cls) -> None:
        """Set block to False."""
        logging.info("Un Blocked.")
        cls._blocked = False

    @classmethod
    def is_blocked(cls) -> bool:
        """
        Get _blocked.

        Returns
        -------
        : bool
            _blocked.
        """
        return cls._blocked

    @classmethod
    def update_quiet_mode(cls, log_level: int) -> None:
        """
        Update the quiet mode based on the log level.

        Parameters
        ----------
        log_level : int
            The set log level for the context manager.
        """
        cls.quiet_mode_enabled = log_level > logging.DEBUG

    @classmethod
    @contextmanager
    def quiet(cls) -> Iterator[None]:
        """
        Make the context quiet unless debug.

        Yields
        ------
        : None
            stdout and stderr are suppressed unless log_level is DEBUG.
        """
        if cls.quiet_mode_enabled:
            with open(os.devnull, "w") as fnull:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = fnull
                sys.stderr = fnull
                try:
                    yield
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
        else:
            yield

    @classmethod
    def config(cls, level: str) -> None:
        """
        Configure the logging system to use RichLogging.

        With support for a custom TRACE level.

        Todo
        ----
        [ ] Implement trace.

        Parameters
        ----------
        level : str
            The logging level to configure. Supports standard levels and TRACE.
        """
        logging.addLevelName(cls.TRACE_LEVEL_NUM, "TRACE")

        logging.basicConfig(
            level=level.upper(),
            format="%(message)s",
            datefmt="[%X]",
            handlers=[cls()],
            force=True,
        )
        RichLogging.update_quiet_mode(logging._nameToLevel[level])
