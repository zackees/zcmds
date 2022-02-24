import os
import sys
import unittest
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


class MainTester(unittest.TestCase):
    def test_imports(self) -> None:
        from static_ffmpeg.run import check_system

        check_system()

    def test_zmcds(self) -> None:
        stdout = check_output("zcmds", shell=True, universal_newlines=True)
        self.assertIn("shrink", stdout)
        self.assertIn("vidclip", stdout)

    @unittest.skipIf(sys.platform == "win32", "win32 test only")
    def test_ls(self) -> None:
        # Tests that ls works on windows.
        stdout = check_output("ls", shell=True, universal_newlines=True)

    def test_folder_existance(self) -> None:
        for d in ALL_DIRS:
            self.assertTrue(os.path.isdir(d), f"{d} is not a directory")


if __name__ == "__main__":
    unittest.main()
