from asyncio import subprocess
import os
import unittest
import subprocess
import sys


class MainTester(unittest.TestCase):
    def test_imports(self) -> None:
        from static_ffmpeg.run import check_system

        check_system()

    def test_zmcds(self) -> None:
        stdout = subprocess.check_output("zcmds", shell=True, universal_newlines=True)
        self.assertIn("shrink", stdout)
        self.assertIn("vidclip", stdout)

    @unittest.skipIf(sys.platform == "win32", "win32 test only")
    def test_ls(self) -> None:
        # Tests that ls works on windows.
        stdout = subprocess.check_output("ls", shell=True, universal_newlines=True)


if __name__ == "__main__":
    unittest.main()
