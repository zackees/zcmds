"""Helper to execute a command."""

import subprocess
import sys


def exec_then_exit(cmd: str) -> None:
    cmd_list = [cmd] + sys.argv[1:]
    rtn = subprocess.call(cmd_list, universal_newlines=True)
    sys.exit(rtn)
