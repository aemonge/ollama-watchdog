#!/usr/bin/env python3

"""Watches a file for changes and appends the changes to another file."""

import os
import time
from pathlib import Path

import yaml
from watchdog.observers import Observer

from src.watch_handler import WatcherHandler

args = {"create-files": True, "keep-input": False}

separators = {
    "pre": '[comment]: # "--- (**{user}** ({date})"\n',
    "post": "\n",
}

if os.getenv("DEBUG") == "True":
    import debugpy

    debugpy.listen(("127.0.0.1", 5678))
    debugpy.wait_for_client()

if __name__ == "__main__":
    config = yaml.safe_load(open("config.yaml", "r"))
    input_file = Path(config["input"])
    output_file = Path(config["output"])
    model_name = config["model"]

    if (not input_file.exists()) and args["create-files"]:
        open(input_file, "w").close()

    if (not output_file.exists()) and args["create-files"]:
        open(output_file, "w").close()

    observer = Observer()
    observer.schedule(
        WatcherHandler(
            src_file=input_file,
            dst_file=output_file,
            separators=separators,
            model_name=model_name,
        ),
        path=str(input_file),  # Watch the directory containing the input file
    )
    observer.start()
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
