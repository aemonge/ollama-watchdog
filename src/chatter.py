"""Here we will define the LLM conversation."""

import asyncio
import logging
import pathlib
from typing import AsyncIterator, List, Optional, Union, cast

from langchain.prompts import PromptTemplate
from langchain_community.llms.vllm import VLLM
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.base import BaseMessage, BaseMessageChunk

from src.models.message_event import MessageEvent, PromptMessage
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


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
            + f"{self.llm.model=}, {self.username=}, and {self.userinfo.name=}"
        )
        prompt_template = PromptTemplate.from_template(
            template=self.template_content, template_format="jinja2"
        )

        return prompt_template.format(
            username=self.username,
            userinfo=self.userinfo_content,
            botname=self.llm.model,
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
        llm: VLLM,
        username: Optional[str] = None,
        enable_stream: bool = False,
    ) -> None:
        """
        Construct the LLM chat with SQLite.

        Parameters
        ----------
        publish : PublisherCallback
            publish a new event to parent
        llm : VLLM
            The model instance.
        username : optional, str
            The name of the user
        enable_stream: bool
            Should the LLM stream the response
        """
        self.llm = llm
        self.enable_stream = enable_stream
        self.username = username or "local-user"

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

        logging.info(f'{self.__class__.__name__} will "ask" "{self.llm.model}"')
        if self.llm.model == "mock":
            response = self._mock_astream()
        else:
            prompt = self.apply_prompt_template(event.contents)
            if self.enable_stream:
                response = self.llm.astream(prompt)
            else:
                response = self.llm.invoke(prompt)

        logging.info(f"{self.__class__.__name__} is handling the response.")
        event = MessageEvent("ai_message", response, self.llm.model)
        logging.info(f'{self.__class__.__name__} is sending ["print", "record"] events')
        logging.debug(event)
        await self.publish(["print", "record"], event)
