"""The prompt and response message class."""

import os
from datetime import datetime
from pathlib import Path
from typing import Iterator, cast
from langchain_community.chat_message_histories import SQLChatMessageHistory

from langchain_core.messages import BaseMessageChunk

from src.llm_query import ask_llm


class Messages:
    """The prompt and response message class."""

    def __init__(
        self,
        separators: dict,
        dst_file: Path,
        src_file: Path,
        model_name: str = "orca-mini",
    ) -> None:
        """
        Initialize the message class.

        Parameters
        ----------
        separators : dict
            The separators to use when writing the file.
        dst_file : Path
            The file to write to.
        src_file : Path
            The file to read form.
        model_name : str
            The LLM model to use.
        """
        self.separators = separators
        self.src_file = src_file
        self.dst_file = dst_file
        self.model_name = model_name
        self.prompt = None

    def _put_title(self, content: str = "system") -> None:
        """
        Put the title in the dst_file.

        Parameters
        ----------
        content : str
            (default: system) The title it self of the message.
        """
        with open(self.dst_file, "a") as output:
            date = datetime.now().strftime("%a, %d %b %H:%M - %Y")
            msg = self.separators["pre"].format(user=content, date=date)
            output.write(msg)

    def _put_content(self, content: str | Iterator[BaseMessageChunk]) -> None:
        """
        Put the title in the dst_file.

        Parameters
        ----------
        content : str | Iterator[Mapping[str, Any]]
            The message or list of messages to put in the file.
        """
        on_stream_end = ""
        with open(self.dst_file, "a", os.O_NONBLOCK) as output:
            if isinstance(content, Iterator):
                for msg in content:
                    on_stream_end += cast(str, msg.content)
                    output.write(cast(str, msg.content))
                    output.flush()
            else:
                output.write(content)

            chat_message_history = SQLChatMessageHistory(
                session_id="test_session_id", connection_string="sqlite:///sqlite.db"
            )
            chat_message_history.add_ai_message(on_stream_end)
            output.write(self.separators["post"])

    def inlcude_prompt(self) -> None:
        """Process the prompt into the output file."""
        self._put_title(content=str(os.getenv("USER")))

        with open(self.src_file, "r") as file:
            self.prompt = file.read()
            if self.prompt is not None and len(self.prompt) > 0:
                self._put_content(content=self.prompt)

    def include_response(self) -> None:
        """Process the response into the output file."""
        if self.prompt is None or len(self.prompt) == 0:
            self._put_title()
            self._put_content(content="# Error\nEmpty prompt file or Empty prompt")
            return

        try:
            title = self.model_name
            msg = ask_llm(self.prompt, model=self.model_name)
        except Exception as e:  # noqa: B902
            title = f"System: Exception {e.__class__.__name__}"
            msg = str(e)
        self._put_title(content=title)
        self._put_content(content=msg)
