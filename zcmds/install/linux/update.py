# pylint: disable=invalid-name

"""
    Update mechanism for darwin (MacOS)
"""

import os
import shutil
import sys

SELF_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(SELF_DIR, "..", ".."))
COMMON_DIR = os.path.join(BASE_DIR, "cmds", "common")
BIN_DIR = os.path.abspath(os.path.join(BASE_DIR, "bin"))


def gen_linux_cmds():
    """Generates commands for MacOS."""
    common_cmds = [
        os.path.abspath(os.path.join(COMMON_DIR, f)) for f in os.listdir(COMMON_DIR)
    ]
    linux_cmds = [
        os.path.abspath(os.path.join(SELF_DIR, f)) for f in os.listdir(SELF_DIR)
    ]
    all_cmds = common_cmds + linux_cmds
    all_cmds = [cmd for cmd in all_cmds if cmd.endswith(".py")]
    shutil.rmtree(BIN_DIR, ignore_errors=True)
    os.makedirs(BIN_DIR, exist_ok=True)
    cmd_set = set([])
    for cmd in all_cmds:
        if cmd in cmd_set:
            sys.stderr.write(
                f"Warning, duplicate found for {os.path.basename(cmd)}, skipping."
            )
        else:
            cmd_set.add(cmd)
        print("making command for " + cmd)
        cmd_name = os.path.basename(cmd)
        out_cmd = os.path.join(BIN_DIR, cmd_name)[0:-3]  # strips .py extension
        with open(out_cmd, encoding="utf-8", mode="wt") as f:
            f.write("python3 " + cmd + "\n")
        # Allow execution on the commands.
        os.system("chmod +x " + out_cmd)


def add_cmds_to_path() -> None:
    """Adds MacOS path to the current environment."""
    needle = f"export PATH=$PATH:{BIN_DIR}"
    bash_profile_file = os.path.expanduser(os.path.join("~", ".bash_profile"))
    if not os.path.exists(bash_profile_file):
        bash_profile = os.path.expanduser(os.path.join("~", ".bashrc"))
    with open(bash_profile_file, encoding="utf-8", mode="rt") as fd:
        bash_profile = fd.read()
    if needle in bash_profile:
        return
    print(f"Attempting to install {BIN_DIR} in {bash_profile_file}")
    lines = bash_profile.splitlines()
    last_path_line = -1
    for i, line in enumerate(lines):
        if "export PATH=" in line:
            last_path_line = i
            continue
    if last_path_line == -1:
        raise ValueError(
            f"Could not find a place to splice in {BIN_DIR}"
            f" into {bash_profile_file}, please do it manually."
        )
    lines.insert(last_path_line + 1, needle)
    # print('\n'.join(lines))
    out_file = "\n".join(lines) + "\n"
    with open(bash_profile_file, encoding="utf-8", mode="wt") as fd:
        fd.write(out_file)

    with open(bash_profile_file, encoding="utf-8", mode="rt") as fd:
        bash_profile = fd.read()
    if needle not in bash_profile:
        raise ValueError(f"{needle} could not be installed into {bash_profile_file}")


def main():
    """Main entry point."""
    gen_linux_cmds()
    add_cmds_to_path()


if __name__ == "__main__":
    main()
