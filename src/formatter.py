"""A module that makes the conversation look pretty."""

from datetime import datetime


class Formatter:
    """Gives format to title, content and more."""

    def __init__(self) -> None:
        """Initialize the Formatter class."""
        self._title = '[comment]: # "--- (**{user}** ({date}))"'

    def title(self, title: str) -> str:
        """
        Print the title, prettier.

        Parameters
        ----------
        title : str
            The raw title

        Returns
        -------
        : str
            A pretty title
        """
        date = datetime.now().strftime("%a, %d %b %H:%M - %Y")
        return self._title.format(user=title, date=date) + "\n\n"
