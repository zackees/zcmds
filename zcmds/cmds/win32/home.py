from ._exec import os_exec

CMD = r"cmd /K cd %HOMEPATH%"


def main() -> int:
    return os_exec(CMD)
