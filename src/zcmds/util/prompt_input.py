"""Prompts for input until two empty lines are entered."""


def prompt_input() -> str:
    lines: list[str] = []
    empty_count = 0
    while True:
        line = input(">>> ")
        if not line:
            empty_count += 1
            if empty_count == 2:
                break
        else:
            empty_count = 0
        lines.append(line)
    return "\n".join(lines)
