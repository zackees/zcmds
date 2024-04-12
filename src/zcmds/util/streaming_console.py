import os
import re
import shutil
import sys
from typing import Optional, Union

import colorama
from colorama import AnsiToWin32
from consolemd import Renderer as ConsoleMDRenderer

colorama.init(wrap=False)

_LINE_UP = "\033[1A"
_LINE_CLEAR = "\x1b[2K"
_LINE_LEFT = "\r"
_term_stdout = AnsiToWin32(sys.stdout, autoreset=True).stream
ansi_escape_regex = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def _num_terminal_cols() -> int:
    cols, _ = shutil.get_terminal_size()
    return cols


def get_options() -> dict:
    options = {
        "end-of-line": "keep",
    }
    return options


def _get_clear_line_sequence(n: int) -> str:
    out = ""
    for _ in range(n):
        out += _LINE_UP + _LINE_CLEAR + _LINE_LEFT
    return out


def count_displaying_characters2(text):
    in_escape_sequence = False
    displaying_char_count = 0

    for char in text:
        if char == "\x1b":  # Start of an ANSI escape sequence
            in_escape_sequence = True
        elif in_escape_sequence and char.isalpha():  # End of an ANSI escape sequence
            in_escape_sequence = False
        elif not in_escape_sequence:  # Counting characters outside of ANSI sequences
            displaying_char_count += 1

    return displaying_char_count


def _count_overflow_lines(text: str, width: int) -> int:
    lines = text.split("\n")
    num_lines = 0
    for line in lines:
        num_display_chars = len(line)
        if num_display_chars > width:
            num_lines += num_display_chars // width
    return num_lines


class MyStream:
    def __init__(self):
        self.buffer = ""

    def write(self, text: str) -> None:
        self.buffer += text

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass

    def read(self) -> str:
        return self.buffer


def _to_consolemd2(text: str) -> str:
    stringio = MyStream()
    style = os.environ.get("CONSOLEMD_STYLE", "native")
    renderer = ConsoleMDRenderer(style_name=style)
    kwargs = {
        "output": stringio,
        "soft_wrap": False,
    }
    renderer.render(text, **kwargs)
    out = stringio.read()
    return out


def _color_print(text: str, delete_lines: Optional[int] = 0) -> str:
    stdout = _to_consolemd2(text=text)
    if delete_lines:
        clear_msg = _get_clear_line_sequence(delete_lines)
        stdout = clear_msg + stdout
    _term_stdout.write(stdout)
    sys.stdout.flush()
    return stdout


class StreamingConsoleMarkdown:
    def __init__(self):
        self.last_written_lines = 0
        self.cols = None
        self.last_written_md = ""

    def update(self, text: str) -> str:
        text = "\n" + text
        cols = self.cols or _num_terminal_cols()
        delete_lines = self.last_written_lines

        # self.last_written_lines = _count_text_lines(text, cols)
        self.last_written_md = _color_print(text, delete_lines=delete_lines)
        lines = self.last_written_md.split("\n")
        n_lines = len(lines) - 1
        n_overflows = _count_overflow_lines(text, cols)
        self.last_written_lines = n_lines + n_overflows
        return self.last_written_md

    def pop_last(self) -> None:
        if self.last_written_lines:
            clear_msg = _get_clear_line_sequence(self.last_written_lines + 1)
            _term_stdout.write("\n" + clear_msg)
            sys.stdout.flush()
            self.last_written_lines = 0
            self.last_written_md = ""

    def _clear_last_line(self) -> None:
        clr_msg = _get_clear_line_sequence(2)
        sys.stdout.write("\n" + clr_msg)
        sys.stdout.flush()


class StreamingConsolePlain:
    def __init__(self):
        self.last_written_text = ""

    def update(self, text: str) -> str:
        n = len(self.last_written_text)
        new_text = text[n:]
        if new_text:
            self.last_written_text = text
            sys.stdout.write(new_text)
            sys.stdout.flush()
        return text


def get_streaming_console() -> Union[StreamingConsoleMarkdown, StreamingConsolePlain]:
    is_windows = os.name == "nt"
    if is_windows:
        is_gitbash = "MSYSTEM" in os.environ
        if is_gitbash:
            return StreamingConsolePlain()
        is_cmd_exe = "ComSpec" in os.environ
        if is_cmd_exe:
            return StreamingConsolePlain()
    return StreamingConsolePlain()


class StreamingConsole:
    def __init__(self) -> None:
        self.impl: Union[StreamingConsoleMarkdown, StreamingConsolePlain] = (
            get_streaming_console()
        )

    def force_color(self) -> None:
        self.impl = StreamingConsoleMarkdown()

    def update(self, text: str) -> None:
        self.impl.update(text)
