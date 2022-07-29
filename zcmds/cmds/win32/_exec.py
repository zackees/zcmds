"""Helper to execute a command."""

import subprocess
import sys
from typing import Optional


def os_exec(cmd: str, inherit_params: bool = True, cwd: Optional[str] = None) -> int:
    cmd_list = [cmd]
    if inherit_params:
        cmd_list += sys.argv[1:]
    rtn = subprocess.call(cmd_list, cwd=cwd, universal_newlines=True)
    return rtn
