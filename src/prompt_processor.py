"""Here we will define the prompt processing."""

import logging

from src.libs.ask_webllm import ask_web_llm
from src.libs.bash_run import bash_run
from src.libs.file_include import replace_include_tags
from src.libs.http_include import get_website_content
from src.libs.remove_comments import remove_comments
from src.libs.web_search import search_online
from src.models.message_event import MessageEvent
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

    async def listen(self, event: MessageEvent) -> None:
        """
        Procese the event and returns the processed event.

        Parameters
        ----------
        event : MessageEvent
            The event to process.
        """
        logging.info("Processing prompt")
        if not isinstance(event.contents, str):
            return

        contents = self._chain_prompt(event.contents)
        logging.debug(contents, "debug")
        logging.info('Sending a "record" event')
        await self.publish(
            ["record"],
            MessageEvent(
                "human_processed_message",
                self.author,
                contents=contents,
            ),
        )
