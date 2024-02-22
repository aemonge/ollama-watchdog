"""Here we will define the prompt processing."""

import logging
from typing import cast

from src.libs.ask_webllm import ask_web_llm
from src.libs.bash_run import bash_run
from src.libs.file_include import replace_include_tags
from src.libs.http_include import get_website_content
from src.libs.remove_comments import remove_comments
from src.libs.web_search import search_online
from src.models.literals_types_constants import ExtendedMessage
from src.models.message_event import MessageEvent, PromptMessage
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class PromptProcessor(PublisherSubscriber):
    """The prompt processor interface."""

    def __init__(
        self,
        author: str,
        publish: PublisherCallback,
    ) -> None:
        """
        Construct the prompt processor.

        Parameters
        ----------
        author : str
            The user name, as author.
        publish : PublisherCallback
            publish a new event to parent
        """
        self.author = author
        self.publish = publish  # type: ignore[reportAttributeAccessIssue]

    def process_prompt(self, prompt: ExtendedMessage) -> ExtendedMessage:
        """
        Process the prompt with several chains.

        Chains
        ------
        remove_comments
            Removes the comments in markdown, to be filter away from the prompt.

        Parameters
        ----------
        prompt : ExtendedMessage
            The raw content from the prompt file.

        Returns
        -------
        : str
            The enhanced and chained prompt
        """
        prompt = cast(str, prompt)
        prompt = remove_comments(prompt)
        return prompt

    def generate_context(self, prompt: ExtendedMessage) -> str:
        """
        Process the prompt with several chains, and enhancers to create context.

        Chains
        ------
        get_website_content
            If a link found inside `<-- http.* -->` it will crawl the website,
            and fetch a summary of the given link as context.
        replace_include_tags
            If a file is found insed `<-- file://.* -->` it will get the file context
            and include them as context.
        search_online
            If a search string is found in `<-- search: .* -->` it will ask duduckgo
            to search and will provide the context of the fist n results
        bash_run
            If a command is found in `<-- run: .* -->` it will run the bash command
            safely, and include the command and results in the context.
        ask_web_llm
            If a query is found in `<-- ask:.* -->` it will use the HTTP LLM to
            ask for query, with perplexity and include the response in the context.

        Parameters
        ----------
        prompt : ExtendedMessage
            The raw content from the prompt file.

        Returns
        -------
        : str
            The context string.
        """
        context = cast(str, prompt)
        context = get_website_content(context)
        context = replace_include_tags(context)
        context = search_online(context)
        context = bash_run(context)
        context = ask_web_llm(context)
        return context

    async def listen(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        logging.info(
            f'PromptProcessor listen "{event.event_type}" and is processing prompt'
        )
        if not isinstance(event.contents, str):
            logging.error("not isinstance(event.contents, str)", event.contents)
            return

        prompt = PromptMessage(self.process_prompt(event.contents))
        prompt.context = self.generate_context(prompt.prompt)

        if isinstance(event.contents, PromptMessage):
            if hasattr(event.contents, "history"):
                prompt.history = event.contents.history
            if hasattr(event.contents, "history_sumarized"):
                prompt.history_sumarized = event.contents.history_sumarized

        event = MessageEvent("human_processed_message", prompt, self.author)
        logging.info('PromptProcessor is sending a "record" event')
        logging.debug(event)
        await self.publish(["record"], event)
