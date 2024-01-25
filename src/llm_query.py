"""Process the contents of the input query file."""

from typing import Any, Iterator, Mapping, cast

from ollama import Client as OClient, Message

from libs.file_include import replace_include_tags
from libs.http_include import get_website_content
from libs.web_search import search_online


def llm_response(prompt: str, model: str) -> Iterator[Mapping[str, Any]]:
    """
    Get the response from a LLM.

    Parameters
    ----------
    prompt : str
        The prompt to send to the LLM.
    model : str
        The LLM model to use.

    Returns
    -------
    : str
        The response from the LLM.
    """
    client = OClient(base_url="http://localhost:11434")
    message = Message(role="user", content=prompt)
    return cast(
        Iterator[Mapping[str, Any]],
        client.chat(model=model, messages=[message], stream=True),
    )


def ask_llm(contents: str, model: str) -> Iterator[Mapping[str, Any]]:
    """
    Process the contents of the input query file.

    Parameters
    ----------
    contents : str
        The contents of the input query file.
    model : str
        The LLM model to use.

    Returns
    -------
    : str
        The processed contents of the input query file.
    """
    prompt = contents
    prompt = get_website_content(prompt)
    prompt = replace_include_tags(prompt)
    prompt = search_online(prompt)

    return llm_response(prompt, model)
