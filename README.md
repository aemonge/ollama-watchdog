# ollama-watchdog

**A Linux daemon that enhances the chat experience in Ollama by handling file includes
and web crawling.**

## Description

`ollama-watchdog` is a Linux daemon designed to integrate with the local LLM manager,
Ollama. It enhances the chat experience by processing markdown files with special syntax
for including files (`<!-- include: file -->`) and web pages
(`<!-- include: http(s)://example.com -->`). This tool aims for simplicity by utilizing
users' preferred editors for input and output handling.

## Usage

To use `ollama-watchdog`, follow these steps:

1. Install the required Python packages (see [Dependencies](#dependencies)).
2. Configure the project by editing the `config.yaml` file (optional).
3. Start the daemon with the following command: `python main.py`.
4. Input your chat messages in a markdown format with file and web include syntax as
   needed.
5. Watch as Ollama processes the message using `ollama-watchdog` to fetch files and web
   pages, if included.

## Features

-   Processes markdown input with special syntax for including files and web pages.
-   Utilizes users' preferred editors for handling input and output.
-   Keeps track of previous conversations (potential future feature).

## Development Plan

### v0.1 (Initial Release)

-   Implement file inclusion functionality using a local file system watcher.
-   Implement web crawling functionality using an existing library like Beautiful Soup
    or Scrapy.

### v0.2 (Improvements)

-   Ensure the daemon can be run as a service or a regular script.
-   Add error handling and logging improvements.
-   Test thoroughly on various Linux distributions.
