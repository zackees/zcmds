import _thread
import logging
import subprocess
import sys


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("grh.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Reset git repository to clean state with git reset --hard && git clean -f.

    This command:
    - Discards all uncommitted changes in tracked files (git reset --hard)
    - Removes all untracked files (git clean -f)

    WARNING: This is a destructive operation and cannot be undone.
    """
    try:
        # Check if git is available
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Error: git is not installed or not in PATH", file=sys.stderr)
            return 1

        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
        )

        if result.returncode != 0:
            print("Error: Not in a git repository", file=sys.stderr)
            return 1

        print("Resetting repository to clean state...")

        # Run git reset --hard
        print("Running: git reset --hard")
        reset_result = subprocess.run(["git", "reset", "--hard"], capture_output=False)

        if reset_result.returncode != 0:
            print("Error: git reset --hard failed", file=sys.stderr)
            return reset_result.returncode

        # Run git clean -f
        print("Running: git clean -f")
        clean_result = subprocess.run(["git", "clean", "-f"], capture_output=False)

        if clean_result.returncode != 0:
            print("Error: git clean -f failed", file=sys.stderr)
            return clean_result.returncode

        print("Repository reset complete!")
        return 0

    except KeyboardInterrupt:
        logger.info("grh interrupted by user")
        _thread.interrupt_main()
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"Error in grh: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
