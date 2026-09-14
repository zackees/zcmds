import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from zcmds.cmds.common import runtest


class TestRuntest(unittest.TestCase):
    """runtest finds the nearest ./test script and runs it with bash."""

    def test_runs_test_script_from_parent_dir(self) -> None:
        project_dir = os.path.join(os.sep, "proj")
        test_script = os.path.join(project_dir, "test")
        bash = Path(os.sep, "bin", "bash")
        with (
            patch.object(sys, "argv", ["runtest", "unit", "fast"]),
            patch.object(runtest.os, "getcwd", return_value=os.path.join(project_dir, "sub")),
            patch.object(runtest, "find_file_in_parents", return_value=(test_script, 1)),
            patch.object(runtest, "find_bash", return_value=bash),
            patch.object(runtest.os, "chdir") as mock_chdir,
            patch.object(runtest.subprocess, "call", return_value=0) as mock_call,
            patch("builtins.print"),
        ):
            result = runtest.main()

        self.assertEqual(result, 0)
        mock_chdir.assert_called_once_with(project_dir)
        mock_call.assert_called_once_with([str(bash), test_script, "unit", "fast"])

    def test_missing_test_script_returns_error(self) -> None:
        with (
            patch.object(sys, "argv", ["runtest"]),
            patch.object(runtest, "find_file_in_parents", return_value=(None, 0)),
            patch.object(runtest.subprocess, "call") as mock_call,
            patch("builtins.print"),
        ):
            result = runtest.main()

        self.assertEqual(result, 1)
        mock_call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
