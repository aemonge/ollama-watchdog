"""
Replaces "run" tags by running in bash the command.

Example
-------
>>> <-- run: "ls" -->
<<< **ls**:
<<<
<<< ```bash
<<< ..
<<< .
<<< example.py
<<< ```
"""

import re
import shlex
import subprocess  # noqa: S404


def bash_run(content: str) -> str:
    """
    Replace content of bash command.

    Parameters
    ----------
    content : str
        The content string to process.

    Returns
    -------
    : str
        The content string with bash output.
    """
    include_pattern = r"(\s*)<--\s*run:\s*\`(.+)\`\s*-->"

    content_list = content.split("\n")
    for i, line in enumerate(content_list):
        if match := re.search(include_pattern, line):
            padding = match[1]
            cmd = shlex.split(match[2])

            try:
                include_content = [
                    f"{padding}{line.rstrip(' ')}\n"
                    for line in (
                        subprocess.check_output(cmd)  # noqa: S603
                        .decode("utf-8")
                        .split("\n")
                    )
                    if line
                ]

            except subprocess.CalledProcessError as e:
                include_content = [
                    "<-- An error occurred while running the command. -->",
                    str(e),
                ]
            code_block = [f"{padding}**{' '.join(cmd)}**:\n\n"]
            code_block += [f"{padding}```bash\n"] + include_content + [f"{padding}```"]
            content_list[i] = "".join(code_block)

    return "\n".join(content_list)
