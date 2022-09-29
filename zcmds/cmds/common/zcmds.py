"""
    Normalizes the audio of a video file.
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
CMD_DIR = os.path.abspath(os.path.dirname(HERE))
BINDINGS_JS_FILE = os.path.join(CMD_DIR, "bindings.json.py")
with open(BINDINGS_JS_FILE, encoding="utf-8", mode="rt") as fd:
    BINDINGS_JSON = json.load(fd)

BINDINGS = BINDINGS_JSON["common"]
if sys.platform == "win32":
    BINDINGS.extend(BINDINGS_JSON["win32"])

if sys.platform == "darwin":
    BINDINGS.extend(BINDINGS_JSON["darwin"])


def main():
    print("zcmds:")
    for binding in sorted(["ytclip"] + BINDINGS):
        print(f"  {binding.split('=')[0]}")


if __name__ == "__main__":
    main()
