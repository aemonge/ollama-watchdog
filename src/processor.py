"""Process the contents of the input query file."""

from langchain_community.llms import Ollama

from libs.file_include import replace_include_tags
from libs.http_include import get_website_content


def llm_response(prompt: str, model: str) -> str:
    """
    Get the response from a LLM.

    https://github.com/jmorganca/ollama/blob/main/docs/tutorials/langchainpy.md

    Todo
    ----
    [ ] Implement by chunks, us check more processor in langchain

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
    ollama = Ollama(base_url="http://localhost:11434", model=model)
    return ollama(prompt)


def process(contents: str, model: str) -> str:
    """
    Process the contents of the input query file.

    Parameters
    ----------
    contents : str
        The contents of the input query file.

    Returns
    -------
    : str
        The processed contents of the input query file.
    """
    prompt = contents
    prompt = get_website_content(prompt)
    prompt = replace_include_tags(prompt)

    return llm_response(prompt, model)
