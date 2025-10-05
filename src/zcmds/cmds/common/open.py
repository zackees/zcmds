import _thread
import logging
import os
import subprocess
import sys
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("open.log"), logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Open a file with the system's default application.
    If the file doesn't exist, prompts the user to create it.
    """
    try:
        if len(sys.argv) < 2:
            print("Usage: open <file>", file=sys.stderr)
            return 1

        file_path = Path(sys.argv[1])

        # Check if file exists
        if not file_path.exists():
            # Prompt user to create the file
            response = (
                input(f"File '{file_path}' does not exist. Create it? [y]/n? ")
                .strip()
                .lower()
            )

            if response == "" or response == "y" or response == "yes":
                # Create the file and any necessary parent directories
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()
                print(f"Created '{file_path}'")
            else:
                print("Operation cancelled", file=sys.stderr)
                return 1

        # Open the file with the system's default application
        if sys.platform == "win32":
            os.startfile(str(file_path))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(file_path)])
        else:  # Linux and other Unix-like systems
            subprocess.run(["xdg-open", str(file_path)])

        return 0

    except KeyboardInterrupt:
        logger.info("open command interrupted by user")
        _thread.interrupt_main()
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"Error in open command: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
