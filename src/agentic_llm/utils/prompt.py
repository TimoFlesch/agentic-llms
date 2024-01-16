import pipes
import re


def convert_to_single_line(code_snippet: str) -> str:
    # from https://stackoverflow.com/a/68203945

    regex = r"^(.+?)#\sBEGIN\s#.+?#\sEND\s#(.+)$"
    core = re.sub(regex, "\\1\\2", code_snippet, 0, re.MULTILINE | re.DOTALL)
    escaped = f"{core!r}"
    outer = pipes.quote(f"exec({escaped})")
    oneline = f"python -c {outer}"
    return oneline
