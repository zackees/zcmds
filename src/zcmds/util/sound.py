"""Sound utilities."""

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
    # Windows needs to convert the mp3 to wav
    add_paths()  # make sure ffprobe/ffmpeg is in PATH
    prev_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            dst = os.path.join(tmpdir, "tmp.wav")
            sound = AudioSegment.from_mp3(file)
            sound.export(dst, format="wav")
            os.chdir(os.path.dirname(dst))
            playsound(os.path.basename(dst), block=True)
    finally:
        os.chdir(prev_cwd)


if __name__ == "__main__":
    beep()
