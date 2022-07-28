from ._exec import os_exec

CMD = r"C:\Program Files\Git\usr\bin\rm.exe"


def main() -> int:
    return os_exec(CMD)
