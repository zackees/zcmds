import sys
import unittest
from subprocess import check_output


def exec(cmd: str) -> str:
    stdout = check_output(cmd, shell=True, universal_newlines=True)
    return stdout


class MainTester(unittest.TestCase):
    def test_imports(self) -> None:
        from static_ffmpeg.run import check_system

        check_system()

    def test_zmcds(self) -> None:
        stdout = exec("zcmds")
        # self.assertIn("shrink", stdout)
        self.assertIn("vidclip", stdout)

    @unittest.skipIf(sys.platform == "win32", "win32 test only")
    def test_ls(self) -> None:
        # Tests that ls works on windows.
        _ = exec("ls")
        _ = exec("which")


if __name__ == "__main__":
    unittest.main()
