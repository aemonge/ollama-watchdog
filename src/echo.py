# echo.py
class Chatter:
    def __init__(self, callback):
        print("Chatter")
        self.callback = callback

    async def process_event(self, event):  # Make this an async function
        await self.callback(f"Received: {event}")
