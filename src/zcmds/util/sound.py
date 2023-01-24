"""Sound utilities."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.abspath(os.path.join(HERE, "..", "assets", "bell.mp3"))


def beep() -> None:
    """Play a beep sound."""
    do_playsound(SOUND_FILE)


def do_playsound(file: str) -> None:
    assert os.path.exists(SOUND_FILE), f"Sound file {SOUND_FILE} does not exist."
    ext = os.path.splitext(file)[1]
    if sys.platform != "win32" or ext == ".wav":
        from playsound import playsound  # type: ignore  # pylint: disable=all

        playsound(file, block=True)
        return
    import winsound  # type: ignore  # pylint: disable=all

    winsound.PlaySound(file, winsound.SND_FILENAME)


if __name__ == "__main__":
    beep()
