"""List serial ports."""

import os
import sys


def execute(cmd: str) -> int:
    """Execute a command."""
    print(cmd)
    return os.system(cmd)


def main() -> None:
    """Try and fix"""
    if sys.platform == "win32":
        execute("ipconfig /flushdns")
        execute("ipconfig /release")
        execute("ipconfig /renew")
    elif sys.platform == "linux":
        execute("sudo systemctl restart network-manager")
    elif sys.platform == "darwin":
        execute("sudo killall -HUP mDNSResponder")
    else:
        print("Unsupported platform")
        return


if __name__ == "__main__":
    main()
