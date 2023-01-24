"""Sound utilities."""

# pylint: disable=all
# mypy: ignore-errors
# flake8: noqa

import os
import sys
import tempfile

from playsound import playsound  # type: ignore
from pydub import AudioSegment  # type: ignore
from static_ffmpeg import add_paths  # type: ignore

HERE = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.abspath(os.path.join(HERE, "..", "assets", "bell.mp3"))


def beep() -> None:
    """Play a beep sound."""
    do_playsound(SOUND_FILE)


def do_playsound(file: str) -> None:
    assert os.path.exists(SOUND_FILE), f"Sound file {SOUND_FILE} does not exist."
    ext = os.path.splitext(file)[1]
    if sys.platform != "win32" or ext == ".wav":
        playsound(file, block=True)
        return
    import winsound  # type: ignore

    winsound.PlaySound(file, winsound.SND_FILENAME)


if __name__ == "__main__":
    beep()
