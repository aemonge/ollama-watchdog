import pathlib
from typing import List
import textwrap

from langchain.prompts import PromptTemplate
from langchain_community.llms.vllm import VLLM

from src.models.literals_types_constants import VLLM_DOWNLOAD_PATH

SEP = "=" * 88


def test_raw(model: str = "TheBloke/laser-dolphin-mixtral-2x7b-dpo-AWQ") -> None:
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


class MSG:
    role: str
    content: str

    def __init__(self, role, content) -> None:
        self.role = role
        self.content = content

    def __str__(self) -> str:
        return f"{self.role}: {self.content}"

    def __repr__(self) -> str:
        return self.__str__()


def test_prompt_template_with_history(
    model: str = "TheBloke/laser-dolphin-mixtral-2x7b-dpo-AWQ",
    disable_llm: bool = False,
) -> None:
    history: List[MSG] = []

    jinja_template = pathlib.Path("./src/prompt_templates/chat.jinja").read_text()
    examples = pathlib.Path("./src/prompt_templates/chat_examples.md").read_text()
    prompt = PromptTemplate.from_template(
        template=jinja_template, template_format="jinja2"
    )

    if not disable_llm:
        llm = VLLM(
            client=None,
            model=model,
            download_dir=VLLM_DOWNLOAD_PATH,
            trust_remote_code=True,  # mandatory for hf models
        )

    print("\n".join([SEP] * 3), end="")

    # ---- First
    query = "Hi, my name is Adrix"
    rendered_prompt = prompt.format(query=query, examples=[examples])
    history.append(MSG("user", query))
    if not disable_llm:
        response = llm.invoke(rendered_prompt)
        print(response)
        history.append(MSG("local-ai", response))
    else:
        history.append(MSG("local-ai", "Nice to meet you, Adrix!"))

    # ---- Second
    print(SEP)
    query = "What's your name?"
    rendered_prompt = prompt.format(query=query, examples=[examples], history=history)
    history.append(MSG("user", query))
    if not disable_llm:
        response = llm.invoke(rendered_prompt)
        print(response)
        history.append(MSG("local-ai", response))
    else:
        history.append(MSG("local-ai", "My name is Carlos the AI Assistant."))

    # ---- Third
    print(SEP)
    query = "Do you remember my name?"
    rendered_prompt = prompt.format(query=query, examples=[examples], history=history)
    history.append(MSG("user", query))
    if not disable_llm:
        response = llm.invoke(rendered_prompt)
        print(response)
        history.append(MSG("local-ai", response))
    else:
        print(rendered_prompt)

    print("\n".join([SEP] * 3), end="")


def test_prompt_template_with_history_and_context(
    model: str = "TheBloke/laser-dolphin-mixtral-2x7b-dpo-AWQ",
    disable_llm: bool = False,
) -> None:
    history: List[MSG] = []

    jinja_template = pathlib.Path("./src/prompt_templates/chat.jinja").read_text()
    examples = pathlib.Path("./src/prompt_templates/chat_examples.md").read_text()
    prompt = PromptTemplate.from_template(
        template=jinja_template, template_format="jinja2"
    )

    if not disable_llm:
        llm = VLLM(
            client=None,
            model=model,
            download_dir=VLLM_DOWNLOAD_PATH,
            trust_remote_code=True,  # mandatory for hf models
        )

    print("\n".join([SEP] * 3), end="")

    context = textwrap.dedent("""\
    "Dulzura Sin Bullying"  https://www.dulzurapr.org
    -------------------------------------------------

    In Puerto Rico, the story of individuals named "Sugarito" unfolds within a complex tapestry of cultural richness and societal challenges. The name, which affectionately translates to "little sugar," carries with it both the sweetness of familial love and the bitterness of societal scrutiny. For those bearing this unique moniker, life is a blend of pride in their identity and resilience against the prejudice they face. The tale of "Sugarito" begins in the vibrant neighborhoods of Puerto Rico, where names are often chosen as a testament to the characteristics parents hope to see in their children or as homage to family traditions. However, in the case of "Sugarito," what was intended as a term of endearment soon became a source of ridicule among peers. Schoolyards, a place of learning and laughter, turned into arenas of mockery, with chants of "Sugarito, dulce pero solito" ("Sugarito, sweet but alone") echoing off the walls. The bullying faced by those named "Sugarito" is not an isolated phenomenon but part of a broader issue of bullying based on perceived differences, as highlighted by StopBullying.gov2

    . These policies emphasize the importance of creating safe and inclusive environments for all students, regardless of their names or backgrounds. The story of "Sugarito" is a poignant reminder of the power of names and the impact of words. It is a call to action for empathy, understanding, and respect in the face of diversity. As Puerto Rico continues to navigate the challenges of bullying and discrimination, the journey of "Sugarito" stands as a testament to the resilience of the human spirit and the enduring sweetness of acceptance.
    """)

    # ---- First
    query = "Hi, my name is Sugarito"
    rendered_prompt = prompt.format(
        query=query, examples=[examples], context=context
    )
    history.append(MSG("user", query))
    if not disable_llm:
        response = llm.invoke(rendered_prompt)
        print(response)
        history.append(MSG("local-ai", response))
    else:
        history.append(MSG("local-ai", "Nice to meet you, Sugarito 👋"))

    # ---- Second
    print(SEP)
    query = "What's your name?"
    rendered_prompt = prompt.format(
        query=query, examples=[examples], history=history, context=context
    )
    history.append(MSG("user", query))
    if not disable_llm:
        response = llm.invoke(rendered_prompt)
        print(response)
        history.append(MSG("local-ai", response))
    else:
        history.append(MSG("local-ai", "My name is Dolphin Mixtral AI 🤖"))

    # ---- Third
    print(SEP)
    query = "Do you remember my name? Every one makes fun of my name 😢"
    rendered_prompt = prompt.format(
        query=query, examples=[examples], history=history, context=context
    )
    history.append(MSG("user", query))
    if not disable_llm:
        response = llm.invoke(rendered_prompt)
        print(response)
        history.append(MSG("local-ai", response))
    else:
        print(rendered_prompt)

    print("\n".join([SEP] * 3), end="")


# test_prompt_template_llmless()
# test_prompt_template()
# test_prompt_template_with_history(disable_llm=True)
# test_prompt_template_with_history_and_context(disable_llm=True)
test_prompt_template_with_history_and_context()
# test_raw()  # noqa: E800
