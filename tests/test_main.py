import os
import sys
import unittest
from ftplib import all_errors
from subprocess import check_output

from zcmds.paths import (
    BASE_DIR,
    BIN_DIR,
    CMD_COMMON_DIR,
    CMD_DARWIN_DIR,
    CMD_DIR,
    CMD_LINUX_DIR,
    CMD_WIN32_DIR,
)

ALL_DIRS = [
    BASE_DIR,
    BIN_DIR,
    CMD_DIR,
    CMD_COMMON_DIR,
    CMD_WIN32_DIR,
    CMD_DARWIN_DIR,
    CMD_LINUX_DIR,
]


def exec(cmd: str) -> str:
    stdout = check_output(cmd, shell=True, universal_newlines=True)
    return stdout


class MainTester(unittest.TestCase):
    def test_imports(self) -> None:
        from static_ffmpeg.run import check_system

        check_system()

    def test_zmcds(self) -> None:
        stdout = exec("zcmds")
        self.assertIn("shrink", stdout)
        self.assertIn("vidclip", stdout)

    @unittest.skipIf(sys.platform == "win32", "win32 test only")
    def test_ls(self) -> None:
        # Tests that ls works on windows.
        _ = exec("ls")

    def test_folder_existance(self) -> None:
        exec("zcmds")
        all_dirs = list(ALL_DIRS)
        all_dirs.remove(BIN_DIR)  # Hack, bin should exist after exec("zcmds")
        for d in ALL_DIRS:
            self.assertTrue(os.path.isdir(d), f"{d} is not a directory")


if __name__ == "__main__":
    unittest.main()
