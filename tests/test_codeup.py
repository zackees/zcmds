import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class CodeupTester(unittest.TestCase):
    def setUp(self):
        """Set up a temporary git repository for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)

        # Create a test file
        with open("test_file.txt", "w") as f:
            f.write("Hello World")

        # Initial commit
        subprocess.run(["git", "add", "test_file.txt"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, capture_output=True)

    def tearDown(self):
        """Clean up the temporary directory."""
        os.chdir(self.original_cwd)
        import shutil
        import stat

        def handle_remove_readonly(func, path, exc):
            """Handle read-only files on Windows."""
            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)

        shutil.rmtree(self.test_dir, onerror=handle_remove_readonly)

    def test_just_ai_commit_flag(self):
        """Test that --just-ai-commit flag works correctly."""
        # Make a change to the file
        with open("test_file.txt", "w") as f:
            f.write("Hello World - Modified")

        # Run codeup with --just-ai-commit and provide a commit message via stdin
        codeup_path = Path(self.original_cwd) / "src" / "zcmds" / "cmds" / "common" / "codeup.py"

        # Test the codeup module by importing it from the source directory
        import sys
        sys.path.insert(0, str(Path(self.original_cwd) / "src"))

        try:
            from zcmds.cmds.common.codeup import main as codeup_main

            # Mock sys.argv for the test
            original_argv = sys.argv
            sys.argv = ["codeup", "--just-ai-commit"]

            # Mock input for commit message
            import builtins
            original_input = builtins.input
            builtins.input = lambda prompt: "Test commit from unit test"

            # Mock API key functions to return None (disable AI)
            from unittest.mock import patch
            with patch('zcmds.cmds.common.openaicfg.get_openai_api_key', return_value=None), \
                 patch('zcmds.cmds.common.openaicfg.get_anthropic_api_key', return_value=None):

                try:
                    result = codeup_main()
                    # Check that the command succeeded
                    self.assertEqual(result, 0, "codeup --just-ai-commit should return 0")

                    # Verify that changes were committed
                    status_result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        capture_output=True,
                        text=True,
                        check=True
                    )

                    # Should be no uncommitted changes
                    self.assertEqual(status_result.stdout.strip(), "", "Working directory should be clean after commit")

                    # Verify the commit was created
                    log_result = subprocess.run(
                        ["git", "log", "--oneline", "-1"],
                        capture_output=True,
                        text=True,
                        check=True
                    )

                    # Should contain our test commit message
                    self.assertIn("Test commit from unit test", log_result.stdout)

                finally:
                    # Restore original input function and argv
                    builtins.input = original_input
                    sys.argv = original_argv

        except ImportError as e:
            self.skipTest(f"Could not import codeup module: {e}")
        finally:
            # Remove the added path
            if str(Path(self.original_cwd) / "src") in sys.path:
                sys.path.remove(str(Path(self.original_cwd) / "src"))


if __name__ == "__main__":
    unittest.main()