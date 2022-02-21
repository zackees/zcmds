import platform
import sys

from zcmds.util.update import update

def main():
    (major, _, _) = platform.python_version_tuple()
    major = int(major)
    if major < 3:
        sys.stderr.write("Please use python 3+\n")
        sys.exit(-1)
    update()

if __name__ == "__main__":
    main()