# echo.py
from src.file_change_event import FileChangeEvent


class Chatter:
    def __init__(self, callback):
        print("Chatter")
        self.callback = callback

    async def process_event(self, event: FileChangeEvent):
        await self.callback(f"Received: {event.contents}")
