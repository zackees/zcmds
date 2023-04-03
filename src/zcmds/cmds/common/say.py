import argparse
import sys
from tempfile import NamedTemporaryFile

from zcmds.util.prompt_input import prompt_input
from zcmds.util.say import say


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="*", help="Text to speak")
    parser.add_argument("--output", "-o", help="Output file")
    args = parser.parse_args()
    text = " ".join(args.text).strip()
    tempmp3 = NamedTemporaryFile(suffix=".mp3", delete=False)
    tempmp3.close()
    if not text:
        text = prompt_input()
        if not text:
            return 1
    say(text, args.output)
    return 0


def main() -> int:
    try:
        return run()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
