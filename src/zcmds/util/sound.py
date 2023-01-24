"""Sound utilities."""

from playaudio import playaudio  # type: ignore
from playaudio.assets.builtin import BELL_MP3  # type: ignore


def beep() -> None:
    """Play a beep sound."""
    playaudio(BELL_MP3)


if __name__ == "__main__":
    beep()
