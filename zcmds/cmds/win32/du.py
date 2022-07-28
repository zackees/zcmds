from ._exec import os_exec

CMD = r"C:\Program Files\Git\usr\bin\du.exe"


def main() -> int:
    return os_exec(CMD)
