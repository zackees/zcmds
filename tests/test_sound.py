import sys
import unittest
from shutil import which
from subprocess import check_output

from zcmds.util.sound import beep


class SoundTester(unittest.TestCase):
    def test_beep(self) -> None:
        beep()


if __name__ == "__main__":
    unittest.main()
