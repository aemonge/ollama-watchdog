"""Manages subscribers and publishes messages."""

import asyncio
import logging
import os
from typing import Dict, List, Optional
from uuid import uuid4

from langchain_community.llms.vllm import VLLM

from src.chains.mute_processing import MuteProcessing
from src.chatter import Chatter
from src.libs.rich_logger import RichLogging
from src.models.literals_types_constants import VLLM_DOWNLOAD_PATH, TopicsLiteral
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherSubscriber
from src.printer import Printer
from src.prompt_processor import PromptProcessor
from src.recorder import Recorder
from src.summarizer import Summarizer
from src.watcher import Watcher


class PubSubOrchestrator(object):
    """Manages subscribers and publishes messages."""

    def _init_llm(self, model: str = "mock") -> None:
        """
        Construct the LLM instance.

        Parameters
        ----------
        model : str
            The model to use for the LLM.
        """
        vllm_kwargs = {
            "gpu_memory_utilization": 0.95,
            "max_model_len": 8192,  # 8192,
            "enforce_eager": True,
        }
        with RichLogging.quiet():
            self.llm = VLLM(
                client=None,
                model=model,
                download_dir=VLLM_DOWNLOAD_PATH,
                callbacks=[MuteProcessing()],
                trust_remote_code=True,  # mandatory for hf models
                vllm_kwargs=vllm_kwargs,
                max_new_tokens=512,  # 512  # noqa: E800
                # cache=False,  # noqa: E800
                # verbose=False,  # noqa: E800
                # top_k=1,  # noqa: E800
                # top_p=0.95,  # noqa: E800
                # temperature=0.8,  # noqa: E800
            )

    def _init_actors(self) -> None:
        """Initialize the main classes."""
        self.printer = Printer(self.publish)
        self.chatter = Chatter(
            self.publish,
            llm=self.llm,
            username=self.user,
            enable_stream=self.enable_stream,
        )
        self.prompt_processor = PromptProcessor(self.user, self.publish)
        self.recorder = Recorder(str(uuid4()), "sqlite:///sqlite.db", self.publish)
        self.summarizer = Summarizer(self.publish, llm=self.llm)
        self.watcher = Watcher(
            self.filename,
            self.user,
            asyncio.get_event_loop(),
            self.publish,
        )

    def __init__(self, prompt_file: str, model: str, enable_stream: bool) -> None:
        """
        Initialize the PubSubOrchestrator.

        Parameters
        ----------
        prompt_file : str
            The file to watch.
        model : str
            The LLM model to use.
        enable_stream: bool
            Should the LLM stream the response
        """
        self.filename = prompt_file
        self.model = model
        self.user = str(os.getenv("USER"))
        self.enable_stream = enable_stream
        self._init_llm(model=self.model)
        self._init_actors()

        self.processed_events: set = set()  # Set to store processed event timestamps

        self.listeners: Dict[TopicsLiteral, list] = {
            "ask": [self.chatter],
            "chain": [self.prompt_processor],
            "print": [self.printer],
            "record": [self.recorder],
            "summarize": [self.summarizer],
        }

    def listen(
        self, topic: TopicsLiteral, subscribers: List[PublisherSubscriber]
    ) -> None:
        """
        Add a subscriber to the orchestrator.

        Parameters
        ----------
        topic: TopicsLiteral
            The topic to subscriber the event from.
        subscribers : List[PublisherSubscriber]
            The subscribers to add.
        """
        for subscriber in subscribers:
            self.listeners[topic].append(subscriber)

    async def publish(
        self, topics: List[TopicsLiteral], event: MessageEvent  # noqa: U100
    ) -> Optional[MessageEvent]:
        """
        Publish the message to all subscribers.

        Parameters
        ----------
        topics: List[TopicsLiteral]
            The topics to subscriber the event from.
        event : MessageEvent
            The event message to publish.
        """
        for topic in topics:
            event_id = f"{topic}-{event.created_at.timestamp()}"
            if event_id not in self.processed_events:
                for subscriber in self.listeners[topic]:
                    await subscriber.listen(event)
                self.processed_events.add(event_id)  # Mark event as processed

    async def start(self) -> None:
        """Asynchronously runs the main program."""
        observer = self.watcher.start_watching()

        try:
            logging.warning("Started Ollama Watch Dog")
            while True:
                await asyncio.sleep(3600)
        finally:
            observer.stop()
