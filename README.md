# ollama-watchdog

**A Linux daemon that enhances the chat experience in Ollama by handling file includes
and web crawling.**

## Description

`ollama-watchdog` is a Linux daemon designed to integrate with the local LLM manager,
Ollama. It enhances the chat experience by processing markdown files with special syntax
for including files (`<!-- include: file -->`) and web pages
(`<!-- include: http(s)://example.com -->`). This tool aims for simplicity by utilizing
users' preferred editors for input and output handling.

## Dependencies

-   (optional) [mdcat](https://github.com/swsnr/mdcat) to visualize the rendered
    markdown files in the terminal.

## Usage

To use `ollama-watchdog`, follow these steps:

1. Install the required Python packages (see [Dependencies](#dependencies)).
2. Configure the project by editing the `config.yaml` file (optional).
3. Start the daemon with the following command: `./main.py`.
4. Input your chat messages in a markdown format with file and web include syntax as
   needed.
5. Watch as Ollama processes the message using `ollama-watchdog` to fetch files and web
   pages, if included.
6. Tail the output file to see real time responses of the chat with `./tail_output`.

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

## Todo

-   [ ] Use the payload option `stream: True` to receive the chunks and process them Use
        a custom mdcat with python, to render markdown properly after all blocks are
        sent
        [help](https://www.perplexity.ai/search/npm-update-g-8J.pqsBFSWOjkWO4nq49UA?s=c)
-   [ ] Analyze https://github.com/microsoft/prompt-engine-py and apply useful ideas
-   [ ] Apply chunks responses to the Ollama
-   [ ] Add support for any endpoint like, perplexity.
-   [ ] Ability to include all types of files
-   [ ] On error, display a message from `system` that tells us the error
-   [ ] Omit commented string to prompt `<!-- -->`
