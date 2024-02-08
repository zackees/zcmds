"""Prompts for input until two empty lines are entered."""

import time


def prompt_input() -> str:
    lines: list[str] = []
    empty_count = 0
    response_times: list[float] = []
    while True:
        start_time = time.time()
        line = input(">>> ")
        if not lines and (line.startswith("!") or line == "exit"):
            return "\n".join(lines + [line])
        diff_time = time.time() - start_time
        response_times.append(diff_time)
        if not line:
            empty_count += 1
            if empty_count == 2:
                last_two = response_times[-2:]
                avg = sum(last_two) / len(last_two)
                if avg < 0.1:
                    empty_count = 0
                else:
                    break
        else:
            empty_count = 0
        lines.append(line)
    return "\n".join(lines)
