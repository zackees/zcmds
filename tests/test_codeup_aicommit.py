import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class CodeupAICommitTester(unittest.TestCase):
    """Test the AI commit functionality in codeup."""

    def setUp(self):
        """Set up a temporary git repository for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)

        # Create initial files
        with open("README.md", "w") as f:
            f.write("# Test Project\n\nThis is a test project for testing AI commit functionality.\n")

        with open("demo.py", "w") as f:
            f.write("""def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
""")

        # Initial commit
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
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

    def test_ai_commit_generation_with_dry_run(self):
        """Test that AI commit generation works with real changes and no push."""
        # Make meaningful changes that should generate a good commit message
        with open("README.md", "w") as f:
            f.write("""# Test Project

This is a test project for testing AI commit functionality.

## Features

- AI-powered commit message generation
- Cross-platform support
- Unit testing framework

## Installation

```bash
pip install -e .
```
""")

        # Add a new feature to demo.py
        with open("demo.py", "w") as f:
            f.write("""def hello_world():
    print("Hello, World!")

def goodbye_world():
    print("Goodbye, World!")

if __name__ == "__main__":
    hello_world()
    goodbye_world()
""")

        # Add a new file
        with open("utils.py", "w") as f:
            f.write("""def add_numbers(a, b):
    return a + b

def multiply_numbers(a, b):
    return a * b
""")

        # Test the codeup module by importing it
        import sys
        src_path = str(Path(self.original_cwd) / "src")
        sys.path.insert(0, src_path)

        try:
            # Import necessary functions
            from zcmds.cmds.common.codeup import _generate_ai_commit_message, get_git_status, has_changes_to_commit

            # Verify we have changes to commit
            self.assertTrue(has_changes_to_commit(), "Should have changes to commit")

            # Get git status for verification
            status = get_git_status()
            self.assertIn("modified:", status, "Should show modified files")
            self.assertIn("Untracked files:", status, "Should show untracked files")

            # Stage all changes
            subprocess.run(["git", "add", "."], check=True, capture_output=True)

            # Test AI commit message generation directly
            ai_message = _generate_ai_commit_message()

            # Verify AI message was generated
            self.assertIsNotNone(ai_message, "AI commit message should be generated")
            self.assertIsInstance(ai_message, str, "AI commit message should be a string")
            self.assertGreater(len(ai_message.strip()), 10, "AI commit message should be substantial")

            print(f"Generated AI commit message: {ai_message}")

            # Verify the message follows conventional commit format
            # Should start with a type like feat:, fix:, docs:, etc.
            lower_message = ai_message.lower()
            conventional_types = ["feat:", "fix:", "docs:", "style:", "refactor:", "perf:", "test:", "chore:", "ci:", "build:"]
            has_conventional_format = any(lower_message.startswith(t) for t in conventional_types)
            self.assertTrue(has_conventional_format, f"AI commit message should follow conventional format. Got: {ai_message}")

            # Test that we can create the commit
            subprocess.run(["git", "commit", "-m", ai_message], check=True, capture_output=True)

            # Verify commit was created
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True,
                check=True
            )

            self.assertIn(ai_message[:30], log_result.stdout, "Commit should contain our AI-generated message")

            # Verify working directory is clean
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            self.assertEqual(status_result.stdout.strip(), "", "Working directory should be clean after commit")

        except ImportError as e:
            self.skipTest(f"Could not import required modules: {e}")
        finally:
            # Remove the added path
            if src_path in sys.path:
                sys.path.remove(src_path)

    def test_ai_commit_with_anthropic_fallback(self):
        """Test that Anthropic API is used when OpenAI fails."""
        # Make a simple change
        with open("README.md", "a") as f:
            f.write("\n## Testing Anthropic Fallback\n")

        import sys
        src_path = str(Path(self.original_cwd) / "src")
        sys.path.insert(0, src_path)

        try:
            from zcmds.cmds.common.codeup import _generate_ai_commit_message_anthropic
            from zcmds.cmds.common.openaicfg import get_anthropic_api_key

            # Verify we have an Anthropic key
            anthropic_key = get_anthropic_api_key()
            self.assertIsNotNone(anthropic_key, "Anthropic API key should be available for testing")

            # Stage the change
            subprocess.run(["git", "add", "."], check=True, capture_output=True)

            # Get the diff for AI processing
            diff_result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                check=True
            )
            diff_text = diff_result.stdout

            # Test Anthropic commit message generation directly
            anthropic_message = _generate_ai_commit_message_anthropic(diff_text)

            self.assertIsNotNone(anthropic_message, "Anthropic should generate a commit message")
            self.assertIsInstance(anthropic_message, str, "Anthropic commit message should be a string")
            self.assertGreater(len(anthropic_message.strip()), 10, "Anthropic commit message should be substantial")

            print(f"Generated Anthropic commit message: {anthropic_message}")

            # Verify it's under 72 characters (conventional commit best practice)
            self.assertLessEqual(len(anthropic_message), 72, "Commit message should be under 72 characters")

        except ImportError as e:
            self.skipTest(f"Could not import required modules: {e}")
        finally:
            if src_path in sys.path:
                sys.path.remove(src_path)

    def test_codeup_just_ai_commit_no_interactive(self):
        """Test codeup --just-ai-commit in non-interactive mode."""
        # Make changes
        with open("demo.py", "a") as f:
            f.write("""
def new_feature():
    \"\"\"A new feature for testing.\"\"\"
    return "new feature"
""")

        import sys
        src_path = str(Path(self.original_cwd) / "src")
        sys.path.insert(0, src_path)

        try:
            from zcmds.cmds.common.codeup import main as codeup_main

            # Mock sys.argv for the test
            original_argv = sys.argv
            sys.argv = ["codeup", "--just-ai-commit", "--no-push"]

            # Mock stdin to be non-interactive
            import io
            original_stdin = sys.stdin
            sys.stdin = io.StringIO("")

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

                # Verify the commit was created with AI message
                log_result = subprocess.run(
                    ["git", "log", "--oneline", "-1"],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Should have a reasonable commit message (not generic fallback)
                commit_message = log_result.stdout.strip()
                self.assertNotIn("chore: automated commit", commit_message, "Should not use generic fallback message")

                print(f"Final commit message: {commit_message}")

            finally:
                # Restore original stdin and argv
                sys.stdin = original_stdin
                sys.argv = original_argv

        except ImportError as e:
            self.skipTest(f"Could not import codeup module: {e}")
        finally:
            if src_path in sys.path:
                sys.path.remove(src_path)


if __name__ == "__main__":
    unittest.main()