"""Task notepad editor - opens ~/Desktop/task.md or ~/task.md in a tkinter editor."""

import _thread
import logging
import sys
from pathlib import Path

from zcmds.util.editor import Editor, ErrorFileHandler


# Configure logging with conditional file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Add stderr handler
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(stderr_handler)

# Add error file handler (only creates file on actual error)
error_file_handler = ErrorFileHandler("task.err")
error_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(error_file_handler)


def find_task_file() -> Path:
    """Find the task file, checking Desktop first, then home directory."""
    try:
        # Try Desktop first
        desktop_path = Path.home() / "Desktop" / "task.md"
        if desktop_path.exists():
            return desktop_path

        # Try home directory
        home_path = Path.home() / "task.md"
        if home_path.exists():
            return home_path

        # Neither exists, create in Desktop
        return desktop_path

    except KeyboardInterrupt:
        logger.info("find_task_file interrupted by user")
        _thread.interrupt_main()
        return Path.home() / "Desktop" / "task.md"
    except Exception as e:
        logger.error(f"Error finding task file: {e}")
        # Default to Desktop
        return Path.home() / "Desktop" / "task.md"


def main() -> int:
    """
    Open the task editor for ~/Desktop/task.md or ~/task.md.

    The editor provides:
    - Line numbers
    - Word wrap
    - Undo/Redo (Ctrl+Z/Ctrl+Y)
    - Font size controls (Ctrl++/Ctrl+-)
    - Auto-save every 30 seconds after editing
    - Status bar with save timestamps
    """
    try:
        task_file = find_task_file()
        editor = Editor(task_file)
        editor.run()
        return 0

    except KeyboardInterrupt:
        logger.info("Task editor interrupted by user")
        print("\nTask editor closed by user", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"Error running task editor: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
