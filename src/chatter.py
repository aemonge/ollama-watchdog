"""Here we will define the LLM conversation."""

import asyncio
import logging
from typing import AsyncIterator, Callable, List, Optional, Union, cast

from langchain_community.llms.vllm import VLLM
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.base import BaseMessage, BaseMessageChunk

from src.libs.rich_logger import RichLogging
from src.models.literals_types_constants import VLLM_DOWNLOAD_PATH, MessageContentType
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


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


class Chatter(PublisherSubscriber):
    """The main chat interface."""

    def _prompt_handler(self, prompts: MessageContentType) -> LanguageModelInput:
        """
        Handle the prompts sent to the LLM.

        Parameters
        ----------
        prompts : MessageContentType
            The prompts sent to the llm

        Raises
        ------
        ValueError
            Prompts are not well typed

        Returns
        -------
        : LanguageModelInput
            The prompts sent to the LLM
        """
        if isinstance(prompts, list) and isinstance(prompts[0], BaseMessage):
            return cast(LanguageModelInput, prompts)

        _msg = f"Chatter detected that prompts are not well typed: {type(prompts):=}"
        logging.error(_msg)
        raise ValueError(_msg)

    async def _response_handler(
        self, prompts: MessageContentType, responses: AsyncIterator[str]
    ) -> AsyncIterator[BaseMessageChunk]:
        """
        Handle the response from the LLM, by removing the prompt from the answer.

        Alternatively
        -------------

            if remaining_prompt.startswith(response):
                remaining_prompt = remaining_prompt[len(response):]
                if not remaining_prompt:
                    prompt_consumed = True
                continue
            else:
                prompt_consumed = True
                yield response

        Parameters
        ----------
        prompts: MessageContentType
            The prompts sent to the llm
        responses: Interator[str]
            The responses from the LLM

        Yields
        ------
        : str | BaseMessageChunk
            The response from the LLM, without the prompt.
        """
        for prompt in cast(list, prompts):
            remaining_prompt = prompt.content
            prompt_length = len(prompt.content)
            first_response = True
            prompt_consumed = False

            async for response in responses:
                if prompt_consumed:
                    yield BaseMessageChunk(type="ai", content=response)

                if first_response:
                    if response.startswith("\n"):
                        response = response[1:]
                    first_response = False

                if not response.startswith(remaining_prompt):
                    yield BaseMessageChunk(type="ai", content=response)

                remaining_prompt = remaining_prompt[len(response) :]
                if not remaining_prompt:
                    prompt_consumed = True
                yield BaseMessageChunk(
                    type="ai", content=response[prompt_length:].strip()
                )

    def __init__(
        self,
        publish: PublisherCallback,
        model: str = "mock",
        response_handler: Optional[Callable] = None,
        prompt_handler: Optional[Callable] = None,
    ) -> None:
        """
        Construct the LLM chat with SQLite.

        Parameters
        ----------
        publish : PublisherCallback
            publish a new event to parent
        model : str
            The model to use for the LLM.
        response_handler: Callable, Optional
            The handling of the response
        prompt_handler: Callable, Optional
            The handling of the prompts
        """
        self.model = model
        self.prompt_handler = (
            self._prompt_handler if prompt_handler is None else prompt_handler
        )
        self.response_handler = (
            self._response_handler if response_handler is None else response_handler
        )

        vllm_kwargs = {
            "gpu_memory_utilization": 0.95,
            "max_model_len": 8192,
            "enforce_eager": True,
        }
        with RichLogging.quiet():
            self.llm = VLLM(
                client=None,
                callbacks=[MuteProcessing()],
                cache=False,
                verbose=False,
                model=model,
                download_dir=VLLM_DOWNLOAD_PATH,
                trust_remote_code=True,  # mandatory for hf models
                vllm_kwargs=vllm_kwargs,
                max_new_tokens=128,  # 512
                top_k=10,
                top_p=0.95,
                temperature=0.8,
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
            response = self._mock_astream()
        elif self.prompt_handler:
            response = self.llm.astream(self.prompt_handler(event.contents))
        else:
            response = self.llm.astream(event.contents)

        if hasattr(self, "response_handler") and self.response_handler is not None:
            response = self.response_handler(
                event.contents, cast(AsyncIterator[str], response)
            )

        event = MessageEvent("ai_message", self.model, contents=response)
        logging.info('Chatter is sending ["print", "record"] events')
        logging.debug(event)
        await self.publish(["print", "record"], event)
