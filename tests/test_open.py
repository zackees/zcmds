import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from zcmds.cmds.common import open as open_cmd

FAKE_SUBL = "/opt/sublime_text/subl"


class TestOpenWithSublime(unittest.TestCase):
    """Text files open in Sublime Text on every platform when it is installed."""

    def _assert_opens_in_sublime(self, platform: str) -> None:
        file_path = Path("x.py")
        with (
            patch.object(sys, "platform", platform),
            patch("shutil.which", return_value=FAKE_SUBL),
            patch.object(open_cmd, "launch_detached") as mock_launch,
            patch.object(open_cmd.subprocess, "run") as mock_run,
        ):
            open_cmd.open_file_with_default_app(file_path)

        mock_launch.assert_called_once_with(
            [Path(FAKE_SUBL), "--new-window", file_path.resolve()]
        )
        mock_run.assert_not_called()

    def test_linux_text_file_opens_in_sublime(self) -> None:
        self._assert_opens_in_sublime("linux")

    def test_darwin_text_file_opens_in_sublime(self) -> None:
        self._assert_opens_in_sublime("darwin")


class TestOpenFallback(unittest.TestCase):
    """Without Sublime, files fall back to the OS default application."""

    def _run_on_linux(
        self, file_path: Path, which_result: str | None
    ) -> tuple[MagicMock, MagicMock]:
        with (
            patch.object(sys, "platform", "linux"),
            patch("shutil.which", return_value=which_result),
            patch.object(open_cmd, "launch_detached") as mock_launch,
            patch.object(open_cmd.subprocess, "run") as mock_run,
        ):
            open_cmd.open_file_with_default_app(file_path)
        return mock_launch, mock_run

    def test_text_file_without_sublime_uses_xdg_open(self) -> None:
        file_path = Path("x.py")
        mock_launch, mock_run = self._run_on_linux(file_path, None)

        mock_launch.assert_not_called()
        mock_run.assert_called_once_with(
            ["xdg-open", str(file_path.resolve())], check=True
        )

    def test_non_text_file_uses_xdg_open_even_with_sublime(self) -> None:
        file_path = Path("doc.pdf")
        mock_launch, mock_run = self._run_on_linux(file_path, FAKE_SUBL)

        mock_launch.assert_not_called()
        mock_run.assert_called_once_with(
            ["xdg-open", str(file_path.resolve())], check=True
        )


class TestSublimeFlag(unittest.TestCase):
    """An explicit --sublime flag errors when Sublime Text is missing."""

    def test_sublime_flag_without_sublime_returns_error(self) -> None:
        fd, tmp_name = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        try:
            with (
                patch.object(sys, "platform", "linux"),
                patch.object(sys, "argv", ["open", "--sublime", tmp_name]),
                patch("shutil.which", return_value=None),
                patch.object(open_cmd, "_sublime_candidates", return_value=[]),
                patch.object(open_cmd, "launch_detached") as mock_launch,
                patch.object(open_cmd.subprocess, "run") as mock_run,
                patch.object(open_cmd.error_file_handler, "emit"),
                patch("sys.stderr") as mock_stderr,
            ):
                result = open_cmd.main()
        finally:
            os.remove(tmp_name)

        self.assertEqual(result, 1)
        mock_launch.assert_not_called()
        mock_run.assert_not_called()
        written = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
        self.assertIn("Sublime Text not found", written)


class TestMacOSOpen(unittest.TestCase):
    """macOS calls /usr/bin/open by absolute path so zcmds' `open` never re-runs itself."""

    def _run_on_darwin(self, func, path: Path) -> MagicMock:
        with (
            patch.object(sys, "platform", "darwin"),
            patch("shutil.which", return_value=None),
            patch.object(open_cmd, "_sublime_candidates", return_value=[]),
            patch.object(open_cmd.subprocess, "run") as mock_run,
        ):
            func(path)
        return mock_run

    def test_directory_uses_system_open(self) -> None:
        path = Path(".")
        mock_run = self._run_on_darwin(open_cmd.open_directory, path)
        mock_run.assert_called_once_with(
            ["/usr/bin/open", str(path.resolve())], check=True
        )

    def test_non_text_file_uses_system_open(self) -> None:
        path = Path("doc.pdf")
        mock_run = self._run_on_darwin(open_cmd.open_file_with_default_app, path)
        mock_run.assert_called_once_with(
            ["/usr/bin/open", str(path.resolve())], check=True
        )

    def test_text_file_without_sublime_uses_system_open(self) -> None:
        path = Path("notes.txt")
        mock_run = self._run_on_darwin(open_cmd.open_file_with_default_app, path)
        mock_run.assert_called_once_with(
            ["/usr/bin/open", str(path.resolve())], check=True
        )


class TestFindSublime(unittest.TestCase):
    """Sublime Text discovery checks PATH first, then platform install locations."""

    def test_prefers_path_lookup(self) -> None:
        with patch("shutil.which", return_value=FAKE_SUBL):
            self.assertEqual(open_cmd.find_sublime(), Path(FAKE_SUBL))

    def test_windows_install_locations_are_checked(self) -> None:
        def exists(self: Path) -> bool:
            return self.name == "sublime_text.exe" and "AppData" in self.parts

        with (
            patch.object(sys, "platform", "win32"),
            patch("shutil.which", return_value=None),
            patch.object(Path, "exists", autospec=True, side_effect=exists),
        ):
            found = open_cmd.find_sublime()

        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.name, "sublime_text.exe")
        self.assertIn("AppData", found.parts)

    def test_macos_app_bundle_is_checked(self) -> None:
        def exists(self: Path) -> bool:
            return "Sublime Text.app" in self.parts

        with (
            patch.object(sys, "platform", "darwin"),
            patch("shutil.which", return_value=None),
            patch.object(Path, "exists", autospec=True, side_effect=exists),
        ):
            found = open_cmd.find_sublime()

        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.name, "subl")

    def test_returns_none_when_missing(self) -> None:
        with (
            patch.object(sys, "platform", "linux"),
            patch("shutil.which", return_value=None),
        ):
            self.assertIsNone(open_cmd.find_sublime())


if __name__ == "__main__":
    unittest.main()
