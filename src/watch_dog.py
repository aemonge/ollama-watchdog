import asyncio
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Watcher(FileSystemEventHandler):
    def __init__(self, filename, loop, callback, filter_duplicated_content=True):
        super().__init__()
        print("Watching")
        self.filename = filename
        self.loop = loop
        self.callback = callback
        self.filter_duplicated_content = filter_duplicated_content
        self.last_content = None

    def on_modified(self, event):
        if event.src_path.endswith(self.filename):
            # Read the contents of the file
            with open(event.src_path, "r") as file:
                current_content = file.read()

            # Check if filtering is enabled and if the content has changed
            if not self.filter_duplicated_content or (
                self.last_content != current_content
            ):
                self.last_content = current_content  # Update the last content
                # Create a dictionary to hold the event data
                event_data = {
                    "type": "fileChanges",
                    "filename": event.src_path,
                    "contents": current_content,
                }
                # Ensure callback is a coroutine function and schedule it to be run
                coroutine = self.callback(event_data)  # This should now be a coroutine
                asyncio.run_coroutine_threadsafe(coroutine, self.loop)
            # If the content is the same and filtering is enabled, do nothing

    def start_watching(self):
        observer = Observer()
        observer.schedule(self, ".", recursive=False)
        observer.start()
        return observer
