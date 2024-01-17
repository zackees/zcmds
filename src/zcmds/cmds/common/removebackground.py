import os
import shutil
import sys
import threading
import time
import webbrowser

PORT = 5283


def install_rembg_if_missing() -> None:
    bin_path = os.path.expanduser("~/.local/bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + bin_path
    if shutil.which("rembg") is not None:
        return
    print("Installing rembg...")
    os.system("pipx install rembg[cli]")
    assert shutil.which("aider") is not None, "aider not found after install"


def open_browser_with_delay(url: str, delay: float) -> None:
    def delayed_open():
        time.sleep(delay)
        webbrowser.open(url)

    threading.Thread(target=delayed_open).start()


def cli() -> int:
    install_rembg_if_missing()
    open_browser_with_delay(f"http://localhost:{PORT}", 4)
    os.system(f"rembg s --port {PORT}")
    return 0


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
