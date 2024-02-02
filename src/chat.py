"""Here we will define the conversation, saving it to SQLite."""

import os
from abc import abstractmethod
from typing import Iterator

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessageChunk

from libs.ask_webllm import ask_web_llm
from libs.bash_run import bash_run
from libs.file_include import replace_include_tags
from libs.http_include import get_website_content
from libs.remove_comments import remove_comments
from libs.web_search import search_online
from src.formatter import Formatter


class Chat:
    """The main chat interface."""

    def __init__(self, session_id: str, connection_string: str, model: str) -> None:
        """
        Construct the LLM chat with SQLite.

        Parameters
        ----------
        session_id : str
            The session ID for the chat.
        connection_string : str
            The connection string for the SQLite database.
        model : str
            The model to use for the LLM.
        """
        self.model = model
        self.user = str(os.getenv("USER"))
        self.history = SQLChatMessageHistory(
            session_id=session_id, connection_string=connection_string
        )
        self.llm = ChatOllama(model=model)
        self.format = Formatter()

    def _chain_prompt(self, prompt: str) -> str:
        """
        Process the prompt with several chains, and enhancers.

        And then saves it in the DB.

        Parameters
        ----------
        prompt : str
            The raw content from the prompt file.

        Returns
        -------
        : str
            The enhanced and chained prompt
        """
        prompt = remove_comments(prompt)
        prompt = get_website_content(prompt)
        prompt = replace_include_tags(prompt)
        prompt = search_online(prompt)
        prompt = bash_run(prompt)
        prompt = ask_web_llm(prompt)
        return prompt

    def ask(self, prompt: str) -> None:
        """
        Process the prompt, saves in database and triggers the LLM.

        Parameters
        ----------
        prompt : str
            The raw content from the prompt file.
        """
        self.send_message(self.format.title(self.user), buffered=False)
        self.send_message(prompt)

        prompt = self._chain_prompt(prompt)
        self.history.add_user_message(prompt)

        self.send_message(self.format.title(self.model), buffered=False)
        self.send_message(self.llm.stream(self.history.messages))

    @abstractmethod
    def send_message(
        self,
        message: str | Iterator[BaseMessageChunk],  # noqa: U100
        buffered: bool = True,  # noqa: U100
    ) -> None:
        """
        Send a message by string or chunks to the terminal.

        Parameters
        ----------
        message : Union[str, Iterator[BaseMessageChunk]]
            The content to append to the conversation file.
        buffered: bool
            (True) If true, saves the message to avoid duplication

        Returns
        -------
        : Iterator[BaseMessageChunk]
            The response from the LLM.
        """
        pass

    def remember(self, response: str) -> None:
        """
        Remember the answer from the AI to keep the conversation fluid.

        Parameters
        ----------
        response : str
            The (finished) response from the AI, un-chunked.
        """
        self.history.add_ai_message(response)
