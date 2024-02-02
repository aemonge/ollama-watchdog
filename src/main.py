"""Main class of the program."""

from pathlib import Path

from src.tail import Tail
from src.watch_dog import Watcher


class Main:
    """Main class of the program."""

    def __init__(self, prompt_file: Path, conversation_file: Path, model: str) -> None:
        """
        Parse the arguments and initialize children.

        Parameters
        ----------
        prompt_file : Path
            The file to watch for prompts.
        conversation_file : Path
            The file to watch for responses.
        model : str
            The model to use.
        """
        self.model = model

        self.watcher = Watcher(
            prompt_file=prompt_file,
            conversation_file=conversation_file,
            on_prompt=self.on_raw_prompt,
            on_respond=self.repond,
        )
        self.tailer = Tail(file=conversation_file)

    def _parse_args(self) -> None:
        """Use Click to parse the arguments."""
        self.prompt_file = Path("input.md")
        self.conversation_file = Path("output.md")

    def run(self) -> None:
        """Run the program."""
        self.watcher.start()
        self.tailer.start()

    def stop(self) -> None:
        """Safely close database and file watcher, to nicely stop the program."""
        pass

    def on_raw_prompt(self, content: str) -> None:
        """
        On raw prompt from file, chat with the LLM.

        Parameters
        ----------
        content : str
            The raw content from the prompt file.
        """
        self.watcher.append_response(content)  # Just echo it for the time being

    def repond(self, content: str) -> None:
        """
        Hold the place to save the response in the DB.

        Parameters
        ----------
        content : str
            The raw response from the LLM.
        """
        print("Save me to DB", content)
