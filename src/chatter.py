"""Here we will define the LLM conversation."""

import asyncio
import logging
from typing import AsyncIterator, List, Union

from langchain_community.llms.vllm import VLLM
from langchain_core.messages import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.base import BaseMessage, BaseMessageChunk
from src.libs.rich_logger import RichLogging

from src.models.literals_types_constants import VLLM_DOWNLOAD_PATH
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Chatter(PublisherSubscriber):
    """The main chat interface."""

    def __init__(
        self,
        publish: PublisherCallback,
        model: str = "mock",
    ) -> None:
        """
        Construct the LLM chat with SQLite.

        Parameters
        ----------
        model : str
            The model to use for the LLM.
        publish : PublisherCallback
            publish a new event to parent
        """
        self.model = model
        with RichLogging.quiet():
            self.llm = VLLM(
                verbose=False,
                client=None,
                model=model,
                download_dir=VLLM_DOWNLOAD_PATH,
                trust_remote_code=True,  # mandatory for hf models
                vllm_kwargs={
                    "gpu_memory_utilization": 0.95,
                    "max_model_len": 1024,  # 4096,  # 8192,
                    "enforce_eager": True,
                },
                max_new_tokens=128,  # 512
            )
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]

    async def _mock_astream(self) -> AsyncIterator[BaseMessageChunk]:
        """
        Mock of the `astream` method, with "hola mundo.".

        Yields
        ------
        AsyncIterator[BaseMessageChunk]
            An asynchronous iterator of BaseMessageChunk objects.
        """
        await asyncio.sleep(0.3)
        yield BaseMessageChunk(type="ai", content="hola ")
        await asyncio.sleep(0.3)
        yield BaseMessageChunk(type="ai", content="mundo")
        await asyncio.sleep(0.3)
        yield BaseMessageChunk(type="ai", content=".")

    def _convert_base_message(
        self, messages: List[BaseMessage]
    ) -> List[Union[HumanMessage, AIMessage]]:
        """
        Convert the BaseMessage to the correct type.

        @deprecated: As soon as there a fix for the typing issue.

        Parameters
        ----------
        messages : List[BaseMessage]
            The list of BaseMessage to convert.

        Returns
        -------
        : List[Union[HumanMessage, AIMessage]]
            The list of HumanMessage or AIMessage objects.
        """
        _messages = []
        for message in messages:
            if message.type == "human":
                _messages.append(HumanMessage(content=message.content))
            elif message.type == "ai":
                _messages.append(AIMessage(content=message.content))
        return _messages

    async def listen(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        if not isinstance(event.contents, list) or not isinstance(
            event.contents[0], BaseMessage
        ):
            msg = f'Type "List[BaseMessage|str]" in {self.__class__.__name__} '
            msg += f"expected: {event.contents}"
            logging.error(msg)
            return

        logging.info(f'Chatting with "{self.model}"')
        if self.model == "mock":
            stream = self._mock_astream()
            await self.publish(
                ["print"],
                MessageEvent("ai_message", self.model, contents=stream),
            )
            logging.info('Streaming the "print" event')
            return

        logging.debug(f"Event: {event}")
        logging.debug(
            f'Event.contents: type "{type(event.contents)}", '
            + f' len "{len(event.contents)}" "'
            + (
                f' type[0] "{type(event.contents[0])}" "'
                if len(event.contents) > 0
                else ""
            )
        )

        with RichLogging.quiet():
            response = self.llm.invoke(event.contents)
        await self.publish(
            ["print"],
            MessageEvent("ai_message", self.model, contents=response),
        )
        logging.info('Streaming the "print" event')
