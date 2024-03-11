#!/usr/bin/env python3

"""The CLI runner for ollama watch dog with a tail."""

import asyncio
import logging
from typing import Optional

import click
from icecream import install
from torch import cuda
from torch.cuda import get_device_properties, set_device
from twisted.internet import asyncioreactor

from src.libs.rich_logger import RichLogging

asyncioreactor.install(asyncio.get_event_loop())

from twisted.internet import reactor  # noqa: E402

install()


@click.command()
@click.argument("prompt_file", default="input.md", type=click.Path(exists=True))
@click.option(
    "--model",
    default="TheBloke/CodeBooga-34B-v0.1-AWQ",
    help="Model to use. Examples: "
    + ",".join(
        [
            "TheBloke/CodeBooga-34B-v0.1-AWQ",
            "TheBloke/laser-dolphin-mixtral-2x7b-dpo-AWQ",
            "mosaicml/mpt-7b",
        ]
    ),
)
@click.option(
    "--log-level",
    type=click.Choice(
        ["TRACE"] + [name for name, _ in logging._nameToLevel.items()],
        case_sensitive=False,
    ),
    default="WARNING",
    help="choose a debug level",
)
@click.option("--cuda-device-id", default=0, type=int, help="choose a debug level")
@click.option(
    "--stream",
    is_flag=True,
    show_default=True,
    default=False,
    type=bool,
    help=(
        "Enable streaming the output. Best if not, but ok if you have a slow "
        + "connection."
    ),
)
def run(
    prompt_file: str,
    model: str,
    log_level: str,
    cuda_device_id: Optional[int],
    stream: bool,
) -> None:
    """
    Ollama Watch-Dog With a Tail, is an utility to create a chat-bot CLI with Ollama.

    Description
    -----------
    It relays on listening to changes in a file and then responding to it to another
    file. By default this command line will be tailing the response file, and providing
    a rich to markdown formatting, allowing an visually pleasant experience in your
    terminal.

    It uses SQLite to create the conversations between the chat and you.

    Besides this, it also enriches the prompt, by allowing special stings that have
    trigger different "chains" in the query:

    Prompt Special tags
    -------------------
    <-- include: file:///tmp.txt --> : Included the `/tmp.txt` file.

    <-- include: https://www.example.com --> : Includes a summary of the site.

    <-- search: a needle --> : Searches in duckduckgo for "a needle".

    <-- ask: a question --> : Asks in perplexity for "a question".

    <-- run: `ls *` : Includes execution and results of the bash command.

    <!-- I'll be ommited --> : Be aware that comments are NOT send to the prompt.


    Usage
    -----
    ollama-dog "prompt.md" "conversation.md" --model="codebooga:34b-v0.1-q5_0"

    Parameters
    ----------
    prompt_file : str
        The file to watch for prompts.
    model : str
        The model to use.
    log_level : str
        The error level to use in logger.
    cuda_device_id : Optional[int]
        The ID of the CUDA device to use.
    no_stream: bool
        Disable streaming the output.
    """
    RichLogging.config(log_level.upper())

    if cuda.is_available():
        cuda.empty_cache()

        if cuda_device_id is not None:
            set_device(cuda_device_id)
            _props = get_device_properties(cuda_device_id)
            logging.info(  # noqa: T201
                f"Cuda device info: {_props.name}, "
                + f"{_props.total_memory / (1024 ** 2):.0f}MB, "
                + f"multi_processor_count={_props.multi_processor_count}"
            )

    from src.pub_sub_orchestrator import PubSubOrchestrator

    orchestrator = PubSubOrchestrator(
        prompt_file=prompt_file, model=model, enable_stream=stream
    )

    asyncio.ensure_future(orchestrator.start())
    reactor.run()  # type: ignore


if __name__ == "__main__":
    run()
