# sourcery skip: no-loop-in-tests

import pathlib

from langchain.prompts import PromptTemplate
from langchain_community.llms.vllm import VLLM

from src.models.literals_types_constants import VLLM_DOWNLOAD_PATH

SEP = "=" * 88


def test_raw(model: str = "TheBloke/laser-dolphin-mixtral-2x7b-dpo-AWQ") -> None:
    """
    A raw example test, that basically checks for GPU size on given model.

    Parameters
    ----------
    model : str
        The model to test.
    """
    llm = VLLM(
        client=None,
        model=model,
        download_dir=VLLM_DOWNLOAD_PATH,
        trust_remote_code=True,  # mandatory for hf models
    )

    query = "What is the capital of France ?"

    print("\n".join([SEP] * 3), end="")
    for _ in range(3):
        print(llm.invoke(query))
        print(SEP)
    print("\n".join([SEP] * 2), end="")


def test_prompt_template_llmless() -> None:
    """
    A example test with prompts and templates.

    Parameters
    ----------
    model : str
        The model to test.
    """
    jinja_template = pathlib.Path("./src/prompt_templates/chat.jinja").read_text()
    examples = pathlib.Path("./src/prompt_templates/chat_examples.md").read_text()
    prompt = PromptTemplate.from_template(
        template=jinja_template, template_format="jinja2"
    )

    context = "This is the current context."
    history = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "ai", "content": "I'm fine, thank you! And you?"},
        {"role": "user", "content": "I'm great, thanks for asking me boss."},
    ]
    query = "What's the capital of France?"

    rendered_prompt = prompt.format(
        context=context, history=history, query=query, examples=[examples]
    )
    print(rendered_prompt)


def test_prompt_template(
    model: str = "TheBloke/laser-dolphin-mixtral-2x7b-dpo-AWQ",
) -> None:
    """
    A example test with prompts and templates.

    Parameters
    ----------
    model : str
        The model to test.
    """
    jinja_template = pathlib.Path("./src/prompt_templates/chat.jinja").read_text()
    examples = pathlib.Path("./src/prompt_templates/chat_examples.md").read_text()
    prompt = PromptTemplate.from_template(
        template=jinja_template, template_format="jinja2"
    )
    llm = VLLM(
        client=None,
        model=model,
        download_dir=VLLM_DOWNLOAD_PATH,
        trust_remote_code=True,  # mandatory for hf models
    )

    query = "What's the capital of France?"

    rendered_prompt = prompt.format(query=query, examples=[examples])

    print("\n".join([SEP] * 3), end="")
    for _ in range(3):
        print(llm.invoke(rendered_prompt))
        print(SEP)
    print("\n".join([SEP] * 2), end="")


# test_prompt_template_llmless()
test_prompt_template()
# test_raw()  # noqa: E800
