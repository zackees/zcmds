import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class Args:
    """Typed arguments for the yolo command."""

    prompt: str | None
    claude_args: List[str]


def parse_args() -> Args:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="yolo",
        description="Launch Claude Code with dangerous mode (--dangerously-skip-permissions). "
        "This bypasses all permission prompts for a more streamlined workflow.",
        epilog="All unknown arguments are passed directly to Claude Code. "
        "WARNING: This mode removes all safety guardrails. Use with caution.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="Run Claude with this prompt and exit when complete",
    )

    # Parse known args, allowing unknown args to be passed to Claude
    known_args, unknown_args = parser.parse_known_args()

    return Args(prompt=known_args.prompt, claude_args=unknown_args)


def main() -> int:
    """
    Launch Claude Code with dangerous mode (--dangerously-skip-permissions).
    This bypasses all permission prompts for a more streamlined workflow.

    WARNING: This mode removes all safety guardrails. Use with caution.
    """
    args = parse_args()

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
        cmd = [claude_path, "--dangerously-skip-permissions"]

        # If prompt is provided, add it to the command
        if args.prompt:
            cmd.extend([args.prompt])

        # Add any additional arguments
        cmd.extend(args.claude_args)

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
