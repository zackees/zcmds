# pylint: skip-file
# mypy: ignore-errors

"""
    Functions to allow manipulation of the windows %PATH% and have it take effect
    to the open command windows.
"""


import sys

if sys.platform != "win32":
    raise OSError("This script is only for windows.")

import argparse
import ctypes
import winreg  # pylint: disable=import-error
from typing import List

REG_PATH_ENV = r"Environment"


def set_user_path(path_value: str) -> bool:
    """Sets the user path and broadcasts the update to all processes."""
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_ENV)
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_PATH_ENV, 0, winreg.KEY_WRITE
        )
        winreg.SetValueEx(registry_key, "Path", 0, winreg.REG_SZ, path_value)
        winreg.CloseKey(registry_key)
        # Now broadcast change to all windows.
        WM_SETTINGCHANGE = 0x1A  # pylint: disable=invalid-name
        HWND_BROADCAST = 0xFFFF  # pylint: disable=invalid-name
        SMTO_ABORTIFHUNG = 0x0002  # pylint: disable=invalid-name
        result = ctypes.c_long()
        SendMessageTimeoutW = (  # pylint: disable=invalid-name
            ctypes.windll.user32.SendMessageTimeoutW  # pylint: disable=invalid-name
        )
        SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result),
        )
        return True
    except BaseException as err:
        print(f"{err}")
        return False


def read_user_path() -> List[str]:
    """Reads the user path from the registry."""
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_PATH_ENV, 0, winreg.KEY_READ
        )
        path, _ = winreg.QueryValueEx(registry_key, "Path")
        winreg.CloseKey(registry_key)
        path_list = [e for e in path.split(";") if e]
        return path_list
    except BaseException as err:
        print(f"{err}")
        return []


def append_user_path_if_not_exist(path: str):
    """Conditionally appends the path, if it doesn't already exist.."""
    all_paths: List[str] = read_user_path()
    if path in all_paths:
        return False
    all_paths_str = ";".join(all_paths)
    all_paths_str = f"{all_paths_str};{path}"
    set_user_path(all_paths_str)
    return True


def main():
    """Main entry point for the command line version of this tool."""
    parser = argparse.ArgumentParser(description="Win32 path management")
    parser.add_argument("--add_path", required=True)
    args = parser.parse_args()
    added = append_user_path_if_not_exist(args.add_path)
    if added:
        print("Added path")
    else:
        print("Already added.")


if __name__ == "__main__":
    main()
