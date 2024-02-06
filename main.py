# At the very top of your main.py, before any other imports
import asyncio
from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())

from twisted.internet import endpoints, reactor
from twisted.protocols import basic
from src.echo import Chatter
from src.watch_dog import Watcher

class PubSubOrchestrator:
    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber):
        self.subscribers.remove(subscriber)

    async def publish(self, message):
        for subscriber in self.subscribers:
            # Ensure that process_event is awaited
            await subscriber.process_event(message)

async def main_async(orchestrator, filename):
    loop = asyncio.get_event_loop()
    # Pass the orchestrator.publish method directly as it is now a coroutine
    watcher = Watcher(filename, loop, orchestrator.publish)
    observer = watcher.start_watching()
    try:
        await asyncio.Event().wait()  # Run forever
    finally:
        observer.stop()

if __name__ == "__main__":
    orchestrator = PubSubOrchestrator()
    # Setup Chatter and add it to the orchestrator
    chatter = Chatter(print)
    orchestrator.add_subscriber(chatter)
    # Start the asyncio event loop with the watcher
    filename = "input.md"
    asyncio.ensure_future(main_async(orchestrator, filename))
    reactor.run()
