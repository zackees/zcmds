"""Sound utilities."""

import os

from playsound import playsound  # type: ignore

HERE = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.abspath(os.path.join(HERE, "..", "assets", "bell.mp3"))


def beep() -> None:
    """Play a beep sound."""

    assert os.path.exists(SOUND_FILE), f"Sound file {SOUND_FILE} does not exist."
    prev_cwd = os.getcwd()
    basedir = os.path.dirname(SOUND_FILE)
    os.chdir(basedir)
    file_name = os.path.basename(SOUND_FILE)
    try:
        playsound(file_name, block=True)
    finally:
        os.chdir(prev_cwd)


if __name__ == "__main__":
    beep()
