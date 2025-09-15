"""Sound utilities."""

import warnings

# Suppress pygame pkg_resources warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning, module="pygame")
    from playaudio import playaudio  # type: ignore
    from playaudio.assets.builtin import BELL_MP3  # type: ignore


def beep() -> None:
    """Play a beep sound."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="playaudio")
        playaudio(BELL_MP3)


if __name__ == "__main__":
    beep()
