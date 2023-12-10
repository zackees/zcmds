import os
import sys
import unittest

from zcmds.version import VERSION

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.dirname(HERE)


def get_setup_version() -> str:
    setup_py = os.path.join(ROOT, "setup.py")
    with open(setup_py, "r") as f:
        # Read the version string from pyproject.toml
        for line in f:
            if "version" in line:
                # version = line.split("=")[1].strip().strip('"').strip("'").strip(",")
                version = (
                    line.split("=")[1].replace('"', "").replace("'", "").replace(",", "").strip()
                )
                break
    return version


class VersionTester(unittest.TestCase):
    def test_version(self) -> None:
        pyproject_version = get_setup_version()
        self.assertEqual(VERSION, pyproject_version)


if __name__ == "__main__":
    unittest.main()
