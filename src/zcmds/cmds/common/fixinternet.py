"""List serial ports."""

import os
import sys


def main() -> None:
    """Try and fix"""
    if sys.platform == "win32":
        os.system("ipconfig /flushdns")
        os.system("ipconfig /release")
        os.system("ipconfig /renew")
    elif sys.platform == "linux":
        os.system("sudo systemctl restart network-manager")
    elif sys.platform == "darwin":
        os.system("sudo killall -HUP mDNSResponder")
    else:
        print("Unsupported platform")
        return


if __name__ == "__main__":
    main()
