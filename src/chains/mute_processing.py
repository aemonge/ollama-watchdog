"""Mute processing "..." chain."""


from langchain_core.callbacks.base import BaseCallbackHandler

from src.libs.rich_logger import RichLogging


class MuteProcessing(BaseCallbackHandler):
    """Mutes the processing progress bar."""

    def on_llm_start(
        self, *args, **kwargs  # noqa: U100, ANN002, ANN003  # pyright: ignore
    ):  # noqa: ANN201, DAR101
        """Mute on start."""
        self.quiet_context = RichLogging.quiet()
        self.quiet_context.__enter__()

    def on_llm_end(
        self, *args, **kwargs  # noqa: U100, ANN002, ANN003  # pyright: ignore
    ):  # noqa: ANN201, DAR101
        """Un-Mute on end."""
        self.quiet_context.__exit__(None, None, None)
