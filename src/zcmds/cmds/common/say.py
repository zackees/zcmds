import argparse
import os
import sys
from tempfile import NamedTemporaryFile

from gtts import gTTS  # type: ignore
from playaudio import playaudio  # type: ignore

from zcmds.util.prompt_input import prompt_input


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="*", help="Text to speak")
    args = parser.parse_args()
    text = " ".join(args.text).strip()
    tempmp3 = NamedTemporaryFile(suffix=".mp3", delete=False)
    tempmp3.close()

    if not text:
        text = prompt_input()
        if not text:
            return 1

    try:
        tts = gTTS(text=text, lang="en")
        tts.save(tempmp3.name)
        playaudio(tempmp3.name)
    finally:
        os.remove(tempmp3.name)
    return 0


def main() -> int:
    try:
        return run()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
