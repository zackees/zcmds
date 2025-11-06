import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from zcmds.util.process import launch_detached


class TestLaunchDetached(unittest.TestCase):
    """Tests for the launch_detached utility."""

    def test_empty_command_raises_error(self) -> None:
        """Test that empty command list raises ValueError."""
        with self.assertRaises(ValueError) as context:
            launch_detached([])

        self.assertIn("Command list cannot be empty", str(context.exception))

    @unittest.skipIf(sys.platform != "win32", "Windows-specific test")
    @patch("shutil.which")
    @patch("subprocess.Popen")
    def test_resolves_executable_in_path(
        self, mock_popen: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that executable is resolved using shutil.which for non-absolute paths."""
        # Mock shutil.which to return a resolved path
        mock_which.return_value = "C:\\Program Files\\App\\app.exe"

        launch_detached(["app", "arg1", "arg2"])

        # Verify shutil.which was called to resolve the executable
        mock_which.assert_called_once_with("app")

        # Verify Popen was called with the resolved path
        mock_popen.assert_called_once()
        call_args, call_kwargs = mock_popen.call_args
        self.assertEqual(call_args[0][0], "C:\\Program Files\\App\\app.exe")
        self.assertEqual(call_args[0][1], "arg1")
        self.assertEqual(call_args[0][2], "arg2")

        # Verify detached process flags
        self.assertIn("creationflags", call_kwargs)
        self.assertEqual(call_kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(call_kwargs["stderr"], subprocess.DEVNULL)
        self.assertEqual(call_kwargs["stdin"], subprocess.DEVNULL)

    @patch("shutil.which")
    def test_executable_not_in_path_raises_error(
        self, mock_which: MagicMock
    ) -> None:
        """Test that FileNotFoundError is raised when executable is not in PATH."""
        # Mock shutil.which to return None (not found)
        mock_which.return_value = None

        with self.assertRaises(FileNotFoundError) as context:
            launch_detached(["nonexistent-app", "arg1"])

        error_msg = str(context.exception)
        self.assertIn("nonexistent-app", error_msg)
        self.assertIn("not found in PATH", error_msg)

    @unittest.skipIf(sys.platform != "win32", "Windows-specific test")
    @patch("subprocess.Popen")
    def test_absolute_path_executable_exists(self, mock_popen: MagicMock) -> None:
        """Test that absolute path to executable is used directly if it exists."""
        # Use a path that actually exists on Windows
        test_path = Path("C:\\Windows\\System32\\notepad.exe")

        if test_path.exists():
            launch_detached([test_path, "arg1"])

            # Verify Popen was called with the absolute path
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0]
            self.assertEqual(call_args[0][0], str(test_path))
            self.assertEqual(call_args[0][1], "arg1")

    def test_absolute_path_executable_not_exists_raises_error(self) -> None:
        """Test that FileNotFoundError is raised for non-existent absolute path."""
        test_path = Path("C:\\NonexistentPath\\app.exe")

        with self.assertRaises(FileNotFoundError) as context:
            launch_detached([test_path, "arg1"])

        error_msg = str(context.exception)
        self.assertIn("Executable not found at specified path", error_msg)
        self.assertIn(str(test_path), error_msg)

    @unittest.skipIf(sys.platform != "win32", "Windows-specific test")
    @patch("shutil.which")
    @patch("subprocess.Popen")
    def test_path_objects_converted_to_strings(
        self, mock_popen: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that Path objects in command are converted to strings."""
        mock_which.return_value = "C:\\Program Files\\App\\app.exe"

        file_path = Path("C:\\test\\file.txt")
        launch_detached(["app", file_path, "arg2"])

        # Verify Popen was called with string arguments
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0]
        self.assertIsInstance(call_args[0][0], str)
        self.assertEqual(call_args[0][1], str(file_path))
        self.assertIsInstance(call_args[0][2], str)

    @unittest.skipIf(sys.platform == "win32", "Unix-specific test")
    @patch("shutil.which")
    @patch("subprocess.Popen")
    def test_unix_uses_start_new_session(
        self, mock_popen: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that Unix systems use start_new_session flag."""
        mock_which.return_value = "/usr/bin/app"

        launch_detached(["app", "arg1"])

        # Verify Popen was called with start_new_session=True
        mock_popen.assert_called_once()
        call_kwargs = mock_popen.call_args[1]
        self.assertTrue(call_kwargs.get("start_new_session"))
        self.assertEqual(call_kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(call_kwargs["stderr"], subprocess.DEVNULL)
        self.assertEqual(call_kwargs["stdin"], subprocess.DEVNULL)


if __name__ == "__main__":
    unittest.main()
