import os
import subprocess
import sys
from pathlib import Path

from download import download  # type: ignore

HERE = Path(__file__).resolve().parent
LOSSLESS_CUT_BINS = HERE / "losslesscut_bins"
BASE_URL = "https://github.com/zackees/losslesscut-bins/raw/main/v3.54.0"
FINISHED = LOSSLESS_CUT_BINS / "finished"

URL = f"{BASE_URL}/win.7z"
BIN_FOLDER = "win"


def unc_path_to_windows_path(path: Path) -> str:
    r"""
    Converts a UNC path like \\localhost\c$\Users\user\Downloads
    to a regular path like C:\Users\user\Downloads.
    """
    path_str = str(path)
    if path_str.startswith("\\\\localhost\\c$"):
        return path_str.replace("\\\\localhost\\c$", "C:", 1)
    return path_str


def main() -> int:
    if sys.platform != "win32":
        raise NotImplementedError(
            f"Lossless cut download not implemented for {sys.platform}"
        )
    os.makedirs(LOSSLESS_CUT_BINS, exist_ok=True)
    filename = Path(URL).name
    target_file = LOSSLESS_CUT_BINS / filename

    if not FINISHED.exists():
        print("Downloading losslesscut...")
        download(URL, str(target_file), replace=False, progressbar=True)

        # Download and extract 7-zip if on Windows
        zip_bin_path = LOSSLESS_CUT_BINS / "7z"
        download(
            "https://github.com/zackees/losslesscut-bins/raw/main/7z/7-zip-win.zip",
            str(zip_bin_path),
            replace=False,
            kind="zip",
            progressbar=True,
        )

        exe_path = zip_bin_path / "7-zip" / "7z.exe"
        assert exe_path.exists(), f"7z.exe not found at {exe_path}"

        # Extracting the downloaded file
        cmd = [str(exe_path), "x", filename]
        subprocess.run(cmd, cwd=str(LOSSLESS_CUT_BINS), check=True)

        # Touch FINISHED file
        with open(FINISHED, "w", encoding="utf-8") as f:
            f.write("finished")

    if sys.platform == "win32":
        lossless_cut_exe = LOSSLESS_CUT_BINS / BIN_FOLDER / "LosslessCut.exe"
        assert (
            lossless_cut_exe.exists()
        ), f"LosslessCut.exe not found at {lossless_cut_exe}"
        lossless_cut_exe_str = unc_path_to_windows_path(lossless_cut_exe)
        cmd = [lossless_cut_exe_str]
        # Add any args that were passed in
        cmd.extend(sys.argv[1:])
        cmd_str = subprocess.list2cmdline(cmd)
        print(f"Launching {cmd_str}")
        # Launch Lossless Cut without blocking the current terminal
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
