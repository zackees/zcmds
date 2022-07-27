# pylint: disable=invalid-name

"""
    Update mechanism for darwin (MacOS)
"""

import os
import sys

SELF_DIR = os.path.dirname(__file__)

# No longer generating MacOS commands, we use the console scripts instead.


def add_python_key_bindings():
    """Adds keybindings to make python development work much better."""
    target_file = os.path.join(
        os.path.expanduser("~"), "Library", "Keybindings", "DefaultKeyBinding.dict"
    )
    if not os.path.exists(target_file):
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, encoding="utf-8", mode="w") as filed:
            filed.write("")
    src_file = os.path.join(SELF_DIR, "macOS_key_bindings.dict")
    with open(src_file, encoding="utf-8", mode="rt") as fd:
        src_file_content = fd.read()
    if not os.path.exists(target_file):
        with open(target_file, encoding="utf-8", mode="rt") as fd:
            fd.write(src_file_content)
            return
    else:
        with open(target_file, encoding="utf-8", mode="rt") as fd:
            target_file_content = fd.read()
        if target_file_content != src_file_content:
            sys.stderr.write(f"Please manually merge {src_file} with {target_file}\n")


def main():
    """Main entry point."""
    # gen_macos_cmds()
    # add_cmds_to_path()
    add_python_key_bindings()


if __name__ == "__main__":
    main()
