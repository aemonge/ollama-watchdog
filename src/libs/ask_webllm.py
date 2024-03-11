"""Searches for a string on the web with search-web."""


import os
import re
from typing import cast

from openai import OpenAI


def ask_web_llm(
    content: str,
) -> str:
    """
    Ask perplexity (or chat gpt-4) for a query and returns the results.

    Parameters
    ----------
    content: str
        The string to search for on the internet.

    Returns
    -------
    : str
        The results from the search, with markdown response syntax.
        to be used as a next step in the conversation.
    """
    api_key: str | None = os.getenv("LLM_API_KEY")
    client: OpenAI = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

    include_pattern = r"(\s*)(<-- *ask: (.*?)(?!-->) *-->)(?!-->)"
    content_list = content.split("\n")

    for i, line in enumerate(content_list):
        if match := re.search(include_pattern, line):
            padding = match[1]
            question = match[3]

            include_content = client.chat.completions.create(
                model="pplx-70b-online",
                messages=[
                    {
                        "role": "system",
                        "content": (  # noqa: PAR001
                            "You are an artificial intelligence assistant"
                            "and you need to engage in a precise, concise, "
                            "focused conversation with another artificial "
                            "intelligence assistant."
                        ),
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
            )
            include_content = cast(str, include_content.choices[0].message.content)

            code_block = [f'**Asking __perplexity llm__ "{question}"**:\n\n']
            include_content = [
                line if i == 0 else padding + line
                for i, line in enumerate(include_content.split("\n"))
            ]
            code_block += include_content + ["\n"]
            content_list[i] = "".join(code_block)

    return "\n".join(content_list)
