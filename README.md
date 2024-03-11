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

## Commands

-   `<-- search: python llm library -->`: Search using duckduckgo python SDK
-   `<-- include: file://~/local/path -->`: Include a local file
-   `<-- include: http(s)://www.example.com -->`: Include a web, using BeautifulSoup
-   `<-- ask: http(s)://www.example.com -->`: Asks in perplexity for "a question".
-   `<-- run: 'command' -->`: Includes execution and results of the bash command.
-   `<!-- I'll be ommited -->` : Be aware that comments are NOT send to the prompt.

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

-   [ ] Fix the summarizer.
-   [x] Must use a chat template.
-   [ ] System manager, for choosing model and templates (modes).
-   [ ] Put caches: https://python.langchain.com/docs/integrations/llms/llm_caching
-   [x] Use the payload option `stream: True` to receive the chunks and process them Use
        a custom mdcat with python, to render markdown properly after all blocks are
        sent.
-   [x] Analyze [prompt-engine-py](https://github.com/microsoft/prompt-engine-py) and
        apply useful ideas.
-   [x] Apply chunks responses to the Ollama.
-   [x] Add support for any endpoint like, perplexity.
-   [ ] Ability to include all types of files, like images.
-   [x] On error, display a message from `system` that tells us the error. Make sure
    https connection errors are being parsed and sent.
-   [x] Omit commented string to prompt `<!-- -->`.
-   [x] Implement and think how to allow Tails to adapt to shorter terminals/console in
        width.
-   [x] After a set amount of time with no response from the server, send the buffer to
        markdown and render it. And quite the tail, and watch the file with watchdog to
        be less resource intensive
-   [x] Use a database to store the conversations.
-   [x] Block the input while the responses are being processed or at least queue it and
        trim duplicated.
-   [x] Use memory for our LLM's https://chatdatabase.github.io/
-   [ ] Allow multi string commands, specially useful for `ask`
-   [ ] Use only GPU, and raise an error if the GPU isn't been used. This should be a
        configuration.
-   [x] On the markdown tail, fix the \`\`\` single with no language marks view
-   [ ] Allow control with special syntax to change the LLM parameters, and SQLite
        session. The idea would be to have a system bot, that can change the main
        threads conversations, drop in and out some actors. Like an director, that
        directs acts (threads) with actors (ai bots). All with the same chat-like
        instructions. Start simple:

            1. list conversations (sessions)
            2. set /switch to session `a`
            3. delete session
            4. set (incognito) ephimeral session (by default?)
            5. change the model

-   [ ] (printer) Stop the buffer on <EOF> or <EOB> block end signals
-   [x] (printer) Fix issue with block code with no language.
-   [x] Detect and avoid the infinite loop.
-   [ ] Implement a simple "working" event that prints a loading spinner in the middle
-   [ ] Move all event triggers and listeners to the orchestrator, to centralize the
        communication and provide a way to log messages pathways.
-   [ ] Use jinja templates for all the context: Ask GPT, web search, etc...

# Notes to organize

-   I've chosen to summarize the messages, when the AI model responds. Since there's
    more delay when the user is thinking on the next question, rather than when to AI
    would be processing.
