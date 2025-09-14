import os
import shutil
import subprocess
import sys


def main() -> int:
    """
    Launch Claude Code with dangerous mode (--dangerously-skip-permissions).
    This bypasses all permission prompts for a more streamlined workflow.

    WARNING: This mode removes all safety guardrails. Use with caution.
    """
    try:
        # Try to find claude in PATH, including common Windows locations
        claude_path = shutil.which("claude")
        if not claude_path:
            # Check common Windows npm global locations
            possible_paths = [
                os.path.expanduser("~/AppData/Roaming/npm/claude.cmd"),
                os.path.expanduser("~/AppData/Roaming/npm/claude.exe"),
                "C:/Users/"
                + os.environ.get("USERNAME", "")
                + "/AppData/Roaming/npm/claude.cmd",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    claude_path = path
                    break

        if not claude_path:
            print("Error: Claude Code is not installed or not in PATH", file=sys.stderr)
            print(
                "Install Claude Code from: https://claude.ai/download", file=sys.stderr
            )
            return 1

        # Build the command with all arguments passed through
        cmd = [claude_path, "--dangerously-skip-permissions"] + sys.argv[1:]

        # Execute Claude with the dangerous permissions flag
        result = subprocess.run(cmd)

        return result.returncode

    except FileNotFoundError:
        print("Error: Claude Code is not installed or not in PATH", file=sys.stderr)
        print("Install Claude Code from: https://claude.ai/download", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error launching Claude: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
