"""Here we will define the LLM conversation."""

import asyncio
import logging
import pathlib
from typing import AsyncIterator, Callable, List, Optional, Union, cast

from langchain.prompts import PromptTemplate
from langchain_community.llms.vllm import VLLM
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.base import BaseMessage, BaseMessageChunk

from src.libs.rich_logger import RichLogging
from src.models.literals_types_constants import VLLM_DOWNLOAD_PATH
from src.models.message_event import MessageEvent, PromptMessage
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

    def apply_prompt_template(self, prompt: PromptMessage) -> LanguageModelInput:
        """
        Handle the prompts sent to the LLM.

        Parameters
        ----------
        prompt : PromptMessage
            The prompts sent to the llm

        Returns
        -------
        : LanguageModelInput
            The prompts sent to the LLM
        """
        logging.info(
            f'Using the "{self.template.name=}" prompt template with: \n'
            + f"{self.model=}, {self.username=}, and {self.userinfo.name=}"
        )
        prompt_template = PromptTemplate.from_template(
            template=self.template_content, template_format="jinja2"
        )

        return prompt_template.format(
            username=self.username,
            userinfo=self.userinfo_content,
            botname=self.model,
            query=prompt.prompt,
            context=prompt.context,
            examples=prompt.examples,
            history=prompt.history,
            history_sumarized=prompt.history_sumarized,
        )

    async def remove_prompt_from_response(
        self, prompts: PromptMessage, responses: AsyncIterator[str]
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
        prompts: PromptMessage
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

    def _set_template(self) -> None:
        """Set the template for the prompt."""
        package_dir = pathlib.Path(__file__).parent
        self.template = package_dir / "prompt_templates" / "chat.jinja"
        self.userinfo = package_dir / "prompt_templates" / "userinfo.txt"
        self.template_content = self.template.read_text()
        self.userinfo_content = self.userinfo.read_text()

    def __init__(
        self,
        publish: PublisherCallback,
        model: str = "mock",
        username: Optional[str] = None,
        enable_stream: bool = False,
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
        username : optional, str
            The name of the user
        enable_stream: bool
            Should the LLM stream the response
        response_handler: Callable, Optional
            The handling of the response
        prompt_handler: Callable, Optional
            The handling of the prompts
        """
        self.model = model
        self.enable_stream = enable_stream
        self.username = username or "local-user"
        self.response_handler = response_handler  # no default response_handler
        self.prompt_handler = (
            self.apply_prompt_template if prompt_handler is None else prompt_handler
        )

        vllm_kwargs = {
            "gpu_memory_utilization": 0.95,
        }
        with RichLogging.quiet():
            self.llm = VLLM(
                client=None,
                callbacks=[MuteProcessing()],
                model=model,
                download_dir=VLLM_DOWNLOAD_PATH,
                trust_remote_code=True,  # mandatory for hf models
                vllm_kwargs=vllm_kwargs,
            )

        self._set_template()
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
        if not isinstance(event.contents, PromptMessage):
            msg = f'Type "PromptMessage" in {self.__class__.__name__} '
            msg += f"expected in event.content: {event=}"
            logging.error(msg)
            return

        logging.info(f'{self.__class__.__name__} will "ask" "{self.model}"')
        if self.model == "mock":
            response = self._mock_astream()
        else:
            prompt = (
                self.prompt_handler(event.contents)
                if self.prompt_handler
                else cast(str, event.contents)
            )
            if self.enable_stream:
                response = self.llm.astream(prompt)
            else:
                response = self.llm.invoke(prompt)

        logging.info(f"{self.__class__.__name__} is handling the response.")
        if hasattr(self, "response_handler") and self.response_handler is not None:
            response = self.response_handler(
                cast(PromptMessage, event.contents), cast(AsyncIterator[str], response)
            )

        event = MessageEvent("ai_message", response, self.model)
        logging.info(f'{self.__class__.__name__} is sending ["print", "record"] events')
        logging.debug(event)
        await self.publish(["print", "record"], event)
