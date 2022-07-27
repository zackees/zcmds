import subprocess
import sys

CMD = r"where"


def main() -> int:
    cmd_list = [CMD] + sys.argv[1:]
    return subprocess.call(cmd_list, universal_newlines=True)


if __name__ == "__main__":
    sys.exit(main())
