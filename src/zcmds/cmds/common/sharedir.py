import os
import sys


def main() -> int:
    try:
        return os.system("ngrok http file:///")
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
