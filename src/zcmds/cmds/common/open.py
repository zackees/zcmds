import _thread
import argparse
import logging
import mimetypes
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


class ErrorFileHandler(logging.Handler):
    """Handler that only creates a log file when an error is logged."""

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename
        self.file_handler: logging.FileHandler | None = None

    def emit(self, record: logging.LogRecord) -> None:
        """Create file handler on first error and emit the record."""
        if self.file_handler is None:
            self.file_handler = logging.FileHandler(self.filename)
            self.file_handler.setFormatter(self.formatter)
        self.file_handler.emit(record)


def is_text_file(file_path: Path) -> bool:
    """
    Determine if a file is a text file.

    Checks:
    1. File extension against known text file extensions
    2. MIME type
    3. Shebang (#!) for files without extensions

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file is a text file, False otherwise
    """
    # List of common text file extensions
    text_extensions = {
        ".txt",
        ".md",
        ".markdown",
        ".log",
        ".cfg",
        ".conf",
        ".ini",
        ".yaml",
        ".yml",
        ".json",
        ".xml",
        ".csv",
        ".tsv",
        ".rst",
        ".tex",
        ".sh",
        ".bash",
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".java",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".less",
        ".sql",
        ".r",
        ".m",
        ".swift",
        ".kt",
        ".kts",
        ".pl",
        ".lua",
        ".vim",
        ".toml",
        ".gitignore",
        ".dockerignore",
        ".editorconfig",
    }

    suffix = file_path.suffix.lower()
    if suffix in text_extensions:
        return True

    # Check MIME type as fallback
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith("text/"):
        return True

    # For files without extensions or unknown types, check file content
    if not suffix or suffix not in text_extensions:
        if not file_path.exists():
            return False

        try:
            with open(file_path, "rb") as f:
                # Read first few bytes for analysis
                first_bytes = f.read(4)

                if not first_bytes:
                    return False

                # Check for shebang (#!)
                if first_bytes[:2] == b"#!":
                    return True

                # Check for BOM (Byte Order Mark) indicating text encoding
                # UTF-8 BOM
                if first_bytes[:3] == b"\xef\xbb\xbf":
                    return True
                # UTF-16 BE BOM
                if first_bytes[:2] == b"\xfe\xff":
                    return True
                # UTF-16 LE BOM
                if first_bytes[:2] == b"\xff\xfe":
                    return True
                # UTF-32 BE BOM
                if first_bytes == b"\x00\x00\xfe\xff":
                    return True
                # UTF-32 LE BOM
                if first_bytes == b"\xff\xfe\x00\x00":
                    return True

        except (OSError, IOError):
            # If we can't read the file, assume it's not a text file
            pass

    return False


def normalize_path(path_str: str) -> Path:
    """
    Normalize a path to handle various formats across different shells.

    Handles:
    - Unix-style tilde expansion (~)
    - Forward and backward slashes
    - Git Bash style paths (/c/Users/... -> C:\\Users\\...)
    - Windows drive letters with forward slashes (C:/Users/... -> C:\\Users\\...)
    """
    # Expand tilde first
    path_str = os.path.expanduser(path_str)

    # Convert Git Bash style paths: /c/path/to/file -> C:\path\to\file
    # Match patterns like /c/, /d/, /e/, etc. at the start
    if sys.platform == "win32":
        match = re.match(r"^/([a-zA-Z])/(.*)$", path_str)
        if match:
            drive_letter = match.group(1).upper()
            rest_of_path = match.group(2)
            path_str = f"{drive_letter}:/{rest_of_path}"

    # Convert to Path object (handles forward/backward slashes automatically)
    return Path(path_str)


def open_directory(dir_path: Path) -> None:
    """
    Open a directory in the system file manager.

    Args:
        dir_path: Path object pointing to the directory to open

    Raises:
        subprocess.CalledProcessError: If the open command fails
        OSError: If the directory cannot be opened
    """
    # Get absolute path
    abs_path = str(dir_path.resolve())

    if sys.platform == "win32":
        # Use Windows ShellExecuteW with 'explore' verb for directories
        # This is more reliable than calling explorer directly
        import ctypes

        result = ctypes.windll.shell32.ShellExecuteW(
            None,  # hwnd (no parent window)
            "explore",  # operation (use 'explore' for directories)
            abs_path,  # directory to open
            None,  # parameters
            None,  # working directory
            1,  # SW_SHOWNORMAL
        )

        # ShellExecuteW returns a value > 32 on success, <= 32 on error
        if result <= 32:
            raise OSError(
                f"Failed to open directory: {abs_path} (ShellExecute error code: {result})"
            )
    elif sys.platform == "darwin":
        subprocess.run(["open", abs_path], check=True)
    else:  # Linux and other Unix-like systems
        subprocess.run(["xdg-open", abs_path], check=True)


def open_file_with_default_app(file_path: Path) -> None:
    """
    Open a file with the system's default application.
    For text files, uses the built-in task editor instead of the OS default.

    Args:
        file_path: Path object pointing to the file to open

    Raises:
        subprocess.CalledProcessError: If the open command fails
        OSError: If the file cannot be opened
    """
    # Check if this is a text file - if so, use our editor
    if is_text_file(file_path):
        from zcmds.util.editor import Editor

        editor = Editor(file_path)
        editor.run()
        return

    # Get absolute path for non-text files
    abs_path = str(file_path.resolve())

    if sys.platform == "win32":
        # Try multiple methods on Windows for best compatibility
        import ctypes

        # Method 1: Try ShellExecuteW first (works for most file types)
        result = ctypes.windll.shell32.ShellExecuteW(
            None,  # hwnd (no parent window)
            "open",  # operation
            abs_path,  # file to open
            None,  # parameters
            None,  # directory
            1,  # SW_SHOWNORMAL
        )

        # ShellExecuteW returns a value > 32 on success, <= 32 on error
        if result > 32:
            return  # Success!

        # Method 2: If ShellExecuteW fails, try os.startfile as fallback
        try:
            import os

            os.startfile(abs_path)
            return  # Success!
        except OSError as e:
            # Both methods failed - provide helpful error message
            error_codes = {
                2: "File not found",
                3: "Path not found",
                5: "Access denied - check file permissions or default application",
                8: "Not enough memory",
                31: "No application associated with this file type",
            }
            error_msg = error_codes.get(result, f"Unknown error (code: {result})")
            raise OSError(
                f"Failed to open '{abs_path}': {error_msg}. "
                f"Original os.startfile error: {e}"
            ) from e
    elif sys.platform == "darwin":
        subprocess.run(["open", abs_path], check=True)
    else:  # Linux and other Unix-like systems
        subprocess.run(["xdg-open", abs_path], check=True)


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
error_file_handler = ErrorFileHandler("open.err")
error_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(error_file_handler)


@dataclass
class OpenArgs:
    """Typed arguments for the open command."""

    path: Path
    create: bool = True


def parse_args() -> OpenArgs:
    """
    Parse command-line arguments.

    Returns:
        OpenArgs dataclass with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Open a file or directory with the system's default application.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  open file.txt              Open a text file in the task editor
  open /c/Users/name/doc.pdf Open a PDF with Git Bash style path
  open ~/Documents           Open a directory in file manager
  open .                     Open current directory
  open --no-create new.txt   Don't prompt to create if file doesn't exist

Keyboard shortcuts in task editor:
  Ctrl+S        Save
  Ctrl+Q        Quit
  Ctrl+W        Toggle line wrapping
  Ctrl++        Increase font size
  Ctrl+-        Decrease font size
  Ctrl+Z        Undo
  Ctrl+Y        Redo
        """,
    )

    parser.add_argument(
        "path",
        type=str,
        help="File or directory to open (supports Unix paths, tilde, Git Bash paths)",
    )

    parser.add_argument(
        "--no-create",
        dest="create",
        action="store_false",
        help="Don't prompt to create file if it doesn't exist",
    )

    args = parser.parse_args()

    # Normalize the path
    normalized_path = normalize_path(args.path)

    return OpenArgs(path=normalized_path, create=args.create)


def main() -> int:
    """
    Open a file or directory with the system's default application.
    If a file doesn't exist, prompts the user to create it (unless --no-create is specified).

    Supports various path formats:
    - Unix-style tilde (~)
    - Forward and backward slashes
    - Git Bash style paths (/c/Users/...)

    For directories:
    - Opens in Windows Explorer (Windows)
    - Opens in Finder (macOS)
    - Opens in default file manager (Linux)

    For text files:
    - Opens in built-in task editor with automatic line wrapping detection

    For other files:
    - Opens with system default application
    """
    try:
        # Parse command-line arguments
        args = parse_args()

        # Check if path exists
        if not args.path.exists():
            if not args.create:
                print(f"Error: '{args.path}' does not exist", file=sys.stderr)
                return 1

            # Only offer to create files, not directories
            response = (
                input(f"File '{args.path}' does not exist. Create it? [y]/n: ")
                .strip()
                .lower()
            )

            if response == "" or response == "y" or response == "yes":
                # Create the file and any necessary parent directories
                args.path.parent.mkdir(parents=True, exist_ok=True)
                args.path.touch()
                print(f"Created '{args.path}'")
            else:
                print("Operation cancelled", file=sys.stderr)
                return 1

        # Handle directories and files differently
        if args.path.is_dir():
            open_directory(args.path)
        else:
            open_file_with_default_app(args.path)

        return 0

    except KeyboardInterrupt:
        logger.info("open command interrupted by user")
        _thread.interrupt_main()
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except SystemExit as e:
        # argparse calls sys.exit() on --help or errors
        code = e.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1  # Fallback for any other type
    except Exception as e:
        logger.error(f"Error in open command: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
