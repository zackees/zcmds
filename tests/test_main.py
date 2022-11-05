import sys
import unittest
from shutil import which
from subprocess import check_output


def exec(cmd: str) -> str:
    stdout = check_output(cmd, shell=True, universal_newlines=True)
    return stdout

def has_cmd(cmd: str) -> bool:
    return which(cmd) is not None

class MainTester(unittest.TestCase):
    def test_imports(self) -> None:
        from static_ffmpeg.run import check_system

        check_system()

    def test_zmcds(self) -> None:
        stdout = exec("zcmds")
        self.assertIn("vidclip", stdout, f"vidclip not found in:\n  {stdout}")

    @unittest.skipIf(sys.platform != "win32", "win32 test only")
    def test_win_cmds(self) -> None:
        # Tests that ls works on windows.
        for cmd in ["ls", "which", "touch"]:
            self.assertTrue(has_cmd(cmd))


if __name__ == "__main__":
    unittest.main()
