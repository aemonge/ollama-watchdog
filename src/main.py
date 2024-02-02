"""Main class of the program."""

from pathlib import Path

from src.chat import Chat
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
        self.tailer = Tail(file=conversation_file)
        self.chat = Chat(
            session_id="test_session_id2",
            connection_string="sqlite:///sqlite.db",
            model=model,
        )
        self.watcher = Watcher(
            prompt_file=prompt_file,
            conversation_file=conversation_file,
            on_prompt=self.chat.ask,
            on_respond=self.chat.remember,
        )
        self.chat.send_message = self.watcher.receive_message

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
