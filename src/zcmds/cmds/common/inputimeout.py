"""
Handles input timeout for Windows and Linux.
"""

# pylint: disable=used-before-assignment

import builtins
import sys

DEFAULT_TIMEOUT = 30.0
INTERVAL = 0.001

SP = " "
CR = "\r"
LF = "\n"
CRLF = CR + LF


class TimeoutOccurred(builtins.Exception):
    pass


def echo(string):
    if string is None:
        return
    sys.stdout.write(string)
    sys.stdout.flush()


def posix_inputimeout(prompt="", timeout=DEFAULT_TIMEOUT):
    if prompt is not None:
        echo(prompt)
    sel = selectors.DefaultSelector()  # type: ignore
    sel.register(sys.stdin, selectors.EVENT_READ)
    events = sel.select(timeout)

    if events:
        key, _ = events[0]
        return key.fileobj.readline().rstrip(LF)
    else:
        echo(LF)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        raise TimeoutOccurred


WIN_BUFFER = ""


def win_inputimeout(prompt="", timeout=DEFAULT_TIMEOUT):
    if prompt is not None:
        echo(prompt)
    begin = time.monotonic()
    end = begin + timeout
    # line = ""
    global WIN_BUFFER

    while time.monotonic() < end:
        if msvcrt.kbhit():
            while c := msvcrt.getwche():
                if c in (CR, LF):
                    echo(CRLF)
                    line = WIN_BUFFER
                    WIN_BUFFER = ""
                    return line
                if c == "\003":
                    WIN_BUFFER = ""
                    raise KeyboardInterrupt
                if c == "\b":
                    WIN_BUFFER = WIN_BUFFER[:-1]
                    cover = SP * len(prompt + WIN_BUFFER + SP)
                    echo("".join([CR, cover, CR, prompt, WIN_BUFFER]))
                else:
                    WIN_BUFFER += c
        time.sleep(INTERVAL)

    echo(CRLF)
    raise TimeoutOccurred


try:
    import msvcrt

except ImportError:
    import selectors
    import termios

    inputimeout = posix_inputimeout

else:
    import time

    inputimeout = win_inputimeout
