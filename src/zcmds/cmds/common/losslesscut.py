import os
import subprocess
import sys

from download import download  # type: ignore

HERE = os.path.abspath(os.path.dirname(__file__))
LOSSLESS_CUT_BINS = os.path.join(HERE, "losslesscut_bins")
BASE_URL = "https://github.com/zackees/losslesscut-bins/raw/main/v3.54.0"
FINISHED = os.path.join(LOSSLESS_CUT_BINS, "finished")


if sys.platform == "win32":
    URL = f"{BASE_URL}/win.7z"
else:
    URL = f"{BASE_URL}/unknown system"
    raise NotImplementedError(
        f"Lossless cut download not implemented for {sys.platform}"
    )


def main() -> int:
    os.makedirs(LOSSLESS_CUT_BINS, exist_ok=True)
    filename = os.path.basename(URL)
    target_file = os.path.join(LOSSLESS_CUT_BINS, filename)
    if not os.path.exists(FINISHED):
        print("Downloading losslesscut...")
        download(URL, target_file, replace=False, progressbar=True)
        if sys.platform == "win32":
            download(
                "https://github.com/zackees/losslesscut-bins/raw/main/7z/7-zip-win.zip",
                os.path.join(LOSSLESS_CUT_BINS, "7z"),
                replace=False,
                kind="zip",
                progressbar=True,
            )
            exe_path = os.path.join("7z", "7-zip", "7z.exe")
            assert os.path.exists(
                os.path.join(LOSSLESS_CUT_BINS, exe_path)
            ), f"7z.exe not found at {exe_path}"
            subprocess.run(
                f"{exe_path} x {filename}",
                shell=True,
                cwd=LOSSLESS_CUT_BINS,
                check=True,
            )
            # touch FINISHED
            with open(FINISHED, encoding="utf-8", mode="w") as f:
                f.write("finished")
    if sys.platform == "win32":
        return os.system(os.path.join(LOSSLESS_CUT_BINS, "win", "LosslessCut.exe"))
    else:
        raise NotImplementedError(
            f"Lossless cut run not implemented for {sys.platform}"
        )


if __name__ == "__main__":
    sys.exit(main())
