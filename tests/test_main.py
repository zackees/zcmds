from asyncio import subprocess
import os
import unittest
import subprocess


class MainTester(unittest.TestCase):
    def test_imports(self) -> None:
        from static_ffmpeg.run import check_system

        check_system()

    def test_zmcds(self) -> None:
        stdout = subprocess.check_output("zcmds", shell=True, universal_newlines=True)
        self.assertIn("shrink", stdout)
        self.assertIn("vidclip", stdout)


if __name__ == "__main__":
    unittest.main()
