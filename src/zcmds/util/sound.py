"""Sound utilities."""

import os
import tempfile

from playsound import playsound  # type: ignore
from pydub import AudioSegment  # type: ignore

HERE = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.abspath(os.path.join(HERE, "..", "assets", "bell.mp3"))


def beep() -> None:
    """Play a beep sound."""

    assert os.path.exists(SOUND_FILE), f"Sound file {SOUND_FILE} does not exist."
    do_playsound(SOUND_FILE)


def do_playsound(file: str) -> None:
    prev_cwd = os.getcwd()
    basedir = os.path.dirname(file)
    os.chdir(basedir)
    file_name = os.path.basename(file)

    with tempfile.TemporaryDirectory() as tmpdir:
        dst = os.path.join(tmpdir, "tmp.wav")
        sound = AudioSegment.from_mp3(file_name)
        sound.export(dst, format="wav")
        try:
            playsound(dst, block=True)
        finally:
            os.chdir(prev_cwd)


if __name__ == "__main__":
    beep()
