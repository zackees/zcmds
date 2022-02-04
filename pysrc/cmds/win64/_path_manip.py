import argparse
import ctypes
import winreg

REG_PATH_ENV = r"Environment"


def set_user_path(value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_ENV)
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_PATH_ENV, 0, winreg.KEY_WRITE
        )
        winreg.SetValueEx(registry_key, "Path", 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        # Now broadcast change to all windows.
        WM_SETTINGCHANGE = 0x1A
        HWND_BROADCAST = 0xFFFF
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
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
    except WindowsError as err:
        print(f"{err}")
        return False


def read_user_path():
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_PATH_ENV, 0, winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(registry_key, "Path")
        winreg.CloseKey(registry_key)
        path_list = [e for e in value.split(";") if e]
        return ";".join(path_list)
    except WindowsError as err:
        print(f"{err}")
        return None


def add_user_path(path):
    all_paths = read_user_path()
    if path in all_paths:
        return False
    all_paths = f"{all_paths};{path}"
    set_user_path(all_paths)
    return True


def main():
    parser = argparse.ArgumentParser(description="Win64 path management")
    parser.add_argument("--add_path", required=True)
    args = parser.parse_args()
    added = add_user_path(args.add_path)
    if added:
        print("Added path")
    else:
        print("Already added.")


if __name__ == "__main__":
    main()
