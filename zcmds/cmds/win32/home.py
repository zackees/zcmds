import os

from zcmds.cmds.win32._exec import os_exec

CMD = r"cmd"


def main() -> int:
    return os_exec(CMD, inherit_params=False, cwd=os.path.expandvars("%HOMEPATH%"))
