"""Sound utilities."""

from playaudio import playaudio  # type: ignore
from playaudio.assets.builtin import BELL_FILE  # type: ignore


def beep() -> None:
    """Play a beep sound."""
    playaudio(BELL_FILE)


if __name__ == "__main__":
    beep()
