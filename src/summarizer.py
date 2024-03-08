"""The class that will store and summarize the history of conversations."""
import logging
import pathlib
from typing import Optional

from langchain.prompts import PromptTemplate
from langchain_community.llms.vllm import VLLM
from langchain_core.language_models.base import LanguageModelInput

from src.models.message_event import MessageEvent, PromptMessage
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class Summarizer(PublisherSubscriber):
    """
    The class that will store and summarize the history of conversations.

    This are the recommended models for summarization:
    * google/mt5-small
    * DistilBERT
    """

    def __init__(
        self,
        publish: PublisherCallback,
        llm: VLLM,
        username: Optional[str] = None,
    ) -> None:
        """
        Summarize with an LLM.

        Parameters
        ----------
        publish : PublisherCallback
            publish a new event to parent
        llm : VLLM
            The model instance.
        username : optional, str
            The name of the user
        """
        package_dir = pathlib.Path(__file__).parent
        self.template = package_dir / "prompt_templates" / "summarize.jinja"
        self.template_content = self.template.read_text()
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]
        self.username = username
        self.llm = llm

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
            + f"{self.llm.model=}, {self.username=}"
        )
        prompt_template = PromptTemplate.from_template(
            template=self.template_content, template_format="jinja2"
        )

        print(prompt.history)

        return prompt_template.format(
            history=prompt.history,
            history_sumarized=prompt.history_sumarized,
            username=self.username,
            botname=self.llm.model,
        )

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

        logging.info(f'{self.__class__.__name__} will "summarize" "{self.llm.model}"')
        prompt = self.apply_prompt_template(event.contents)
        response = self.llm.invoke(prompt)
        # print(response)

        event = MessageEvent("chat_summary", response, self.llm.model)
        logging.info(f'{self.__class__.__name__} is sending ["record"] event')
        logging.debug(event)
        await self.publish(["record"], event)
