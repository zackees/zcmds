import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from zcmds.cmds.common import vid2mp4


class Vid2Mp4Tester(unittest.TestCase):
    def test_nvenc_uses_constqp_quality_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "input.mkv"
            input_path.write_bytes(b"")

            with patch("zcmds.cmds.common.vid2mp4.subprocess.run") as mock_run:
                mock_run.return_value = subprocess.CompletedProcess([], 0)
                with redirect_stdout(io.StringIO()):
                    result = vid2mp4.main([str(input_path), "--nvenc"])

            self.assertEqual(0, result)
            command = mock_run.call_args.args[0]
            self.assertIn("-rc", command)
            self.assertIn("constqp", command)
            self.assertIn("-qp", command)
            self.assertIn("23", command)
            self.assertNotIn("-cq", command)

    def test_x264_uses_crf_quality_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "input.mkv"
            input_path.write_bytes(b"")

            with patch("zcmds.cmds.common.vid2mp4.subprocess.run") as mock_run:
                mock_run.return_value = subprocess.CompletedProcess([], 0)
                with redirect_stdout(io.StringIO()):
                    result = vid2mp4.main([str(input_path)])

            self.assertEqual(0, result)
            command = mock_run.call_args.args[0]
            self.assertIn("libx264", command)
            self.assertIn("-crf", command)
            self.assertIn("23", command)
            self.assertNotIn("-rc", command)

    def test_ffmpeg_failure_returned_without_generated_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "input.mkv"
            input_path.write_bytes(b"")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch("zcmds.cmds.common.vid2mp4.subprocess.run") as mock_run:
                mock_run.return_value = subprocess.CompletedProcess([], 9)
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    result = vid2mp4.main([str(input_path)])

            self.assertEqual(9, result)
            self.assertNotIn("Generated", stdout.getvalue())
            self.assertIn("ffmpeg failed with exit code 9", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
