import os
import sys
import unittest

from zcmds.version import VERSION

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.dirname(HERE)


def get_pyproject_version() -> str:
    pyproject_file = os.path.join(ROOT, "pyproject.toml")
    with open(pyproject_file, "r") as f:
        # Read the version string from pyproject.toml
        for line in f:
            if line.startswith("version"):
                version = line.split("=")[1].strip().strip('"')
                break
    return version


class VersionTester(unittest.TestCase):
    def test_version(self) -> None:
        pyproject_version = get_pyproject_version()
        self.assertEqual(VERSION, pyproject_version)


if __name__ == "__main__":
    unittest.main()
