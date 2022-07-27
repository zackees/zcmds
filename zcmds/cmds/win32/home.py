
from ._exec import exec_then_exit

CMD = r"cmd /K cd %HOMEPATH%"
if __name__ == "__main__":
    exec_then_exit(CMD)
