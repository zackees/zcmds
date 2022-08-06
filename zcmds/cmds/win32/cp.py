from zcmds.cmds.win32._exec import os_exec

CMD = r"C:\Program Files\Git\usr\bin\cp.exe"


def main() -> int:
    return os_exec(CMD)
