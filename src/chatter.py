"""Here we will define the LLM conversation."""

import asyncio
import logging
from typing import AsyncIterator, List, Union

from langchain.chains import LLMChain
from langchain_community.llms.vllm import VLLM
from langchain_core.callbacks.base import BaseCallbackHandler, BaseCallbackManager
from langchain_core.messages import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.base import BaseMessage, BaseMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.config import RunnableConfig

from src.libs.rich_logger import RichLogging
from src.models.literals_types_constants import VLLM_DOWNLOAD_PATH
from src.models.message_event import MessageEvent
from src.models.publish_subscribe_class import PublisherCallback, PublisherSubscriber


class MuteProcessing(BaseCallbackHandler):
    """Mutes the processing progress bar."""

    def on_llm_start(self, *args, **kwargs):
        """Mute on start."""
        self.quiet_context = RichLogging.quiet()
        self.quiet_context.__enter__()

    def on_llm_end(self, *args, **kwargs):
        """Un-Mute on end."""
        self.quiet_context.__exit__(None, None, None)


class FilterQuestionHandler(BaseCallbackHandler):
    def on_llm_response(self, response: str, **kwargs) -> str:
        print("on_llm_response")

    # def on_llm_start(self, *args, **kwargs):
    #     print("on_llm_start (suppressed processing....)")
    #     self.quiet_context = RichLogging.quiet()
    #     self.quiet_context.__enter__()
    #
    # def on_llm_end(self, *args, **kwargs):
    #     self.quiet_context.__exit__(None, None, None)
    #     print("on_llm_end")

    def on_llm_new_token(self, token: str, **kwargs):
        print("on_llm_new_token")

    def on_llm_error(self, error: str, **kwargs):
        print("on_llm_error")

    def on_chain_start(self, *args, **kwargs):
        print("on_chain_start")

    def on_chain_end(self, *args, **kwargs):
        print("on_chain_end")

    def on_chain_error(self, error: str, **kwargs):
        print("on_chain_error")

    def on_tool_start(self, *args, **kwargs):
        print("on_tool_start")

    def on_tool_end(self, *args, **kwargs):
        print("on_tool_end")

    def on_tool_error(self, error: str, **kwargs):
        print("on_tool_error")

    def on_buffer_token(self, token: str, **kwargs):
        print("on_buffer_token")

    def on_retriever_end(self, error: str, **kwargs):
        print("on_retriever_end")

    def on_retriever_start(self, error: str, **kwargs):
        print("on_retriever_start")

    def on_agent_action(self, *args, **kwargs):
        print("on_agent_action")

    def on_text(self, *args, **kwargs):
        print("on_text")


class Chatter(PublisherSubscriber):
    """The main chat interface."""

    def _hey_(self):
        # prompt = ChatPromptTemplate.from_template("{input}")
        # example_prompt = ChatPromptTemplate.from_messages(
        #     [
        #         ("human", "{input}"),
        #         ("ai", "{output}"),
        #     ]
        # )

        # chain = prompt | self.llm
        # with RichLogging.quiet():
        # r = chain.stream({"input": "What is the capital of France ?"})
        # r = self.llm.stream("What is the capital of France ?")
        r = self.llm.invoke("What is the capital of France ?")

        print("==========================")
        print(r)
        # for a in r:
        #     print(a)

        # from langchain.chains import LLMChain
        # from langchain.prompts import PromptTemplate
        #
        # template = """Question: {question}
        #
        # Answer: Let's think step by step."""
        # prompt = PromptTemplate.from_template(template)
        #
        # llm_chain = LLMChain(prompt=prompt, llm=llm)
        #
        # question = "Who was the US president in the year the first Pokemon game was released?"
        #
        # print(llm_chain.invoke(question))
        print("======================================================================")

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
        print("======================================================================")
        self.model = model
        with RichLogging.quiet():
            self.llm = VLLM(
                client=None,
                callbacks=[MuteProcessing(), FilterQuestionHandler()],
                verbose=False,
                model=model,
                download_dir=VLLM_DOWNLOAD_PATH,
                trust_remote_code=True,  # mandatory for hf models
                vllm_kwargs={
                    "gpu_memory_utilization": 0.95,
                    "max_model_len": 1024,  # 4096,  # 8192,
                    "enforce_eager": True,
                },
                max_new_tokens=128,  # 512
                top_k=10,
                top_p=0.95,
                temperature=0.8,
            )

        self._hey_()
        return None
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

        logging.warning(f'Chatting with "{self.model}"')
        if self.model == "mock":
            response = self._mock_astream()
        else:
            with RichLogging.quiet():
                response = self.llm.invoke(event.contents)

        event = MessageEvent("ai_message", self.model, contents=response)
        logging.warning('Chatter is sending a "print" event')
        logging.info(event)
        await self.publish(["print"], event)
