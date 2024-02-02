"""Here we will define the conversation, saving it to SQLite."""

from abc import abstractmethod
from typing import Iterator

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessageChunk


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
        self.history = SQLChatMessageHistory(
            session_id=session_id, connection_string=connection_string
        )
        self.llm = ChatOllama(model=model)

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
        return prompt

    def ask(self, prompt: str) -> None:
        """
        Process the prompt, saves in database and triggers the LLM.

        Parameters
        ----------
        prompt : str
            The raw content from the prompt file.
        """
        prompt = self._chain_prompt(prompt)
        self.history.add_user_message(prompt)
        self.respond(self.llm.stream(self.history.messages))

    @abstractmethod
    def respond(self, message: str | Iterator[BaseMessageChunk]) -> None:  # noqa: U100
        """
        Save the response in the DB, and respond.

        Parameters
        ----------
        message : Union[str, Iterator[BaseMessageChunk]]
            The content to append to the conversation file.

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
