"""Helper to execute a command."""

import subprocess
import sys


def os_exec(cmd: str) -> int:
    cmd_list = [cmd] + sys.argv[1:]
    rtn = subprocess.call(cmd_list, universal_newlines=True)
    return rtn
