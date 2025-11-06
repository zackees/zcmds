"""
Process management utilities for launching detached processes.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def launch_detached(command: list[str | Path]) -> None:
    """
    Launch a command in a detached process that doesn't block the terminal.

    This function starts a process that runs completely independently of the parent
    terminal. The terminal returns control immediately, and the process continues
    running even if the terminal is closed.

    The executable is resolved before launching to ensure it exists and provide
    clear error messages if it's not found.

    Cross-platform implementation:
    - Windows: Uses DETACHED_PROCESS and CREATE_NEW_PROCESS_GROUP flags
    - Unix-like: Uses start_new_session=True

    Args:
        command: List of command arguments (e.g., ["sublime_text.exe", "file.txt"])
                 Can contain strings or Path objects, which will be converted to strings
                 The first argument is the executable name or path

    Raises:
        FileNotFoundError: If the executable cannot be found in PATH or at the specified path
        ValueError: If command list is empty

    Example:
        >>> launch_detached(["notepad.exe", "file.txt"])
        >>> # Terminal is immediately ready for next command
        >>> # Notepad runs independently

        >>> launch_detached([Path("/usr/bin/vim"), "file.txt"])
        >>> # Works with Path objects too

    Notes:
        - All stdio (stdin, stdout, stderr) is redirected to DEVNULL
        - Process is completely detached from the parent's terminal
        - No zombie processes - proper process management with Popen
        - Works across Windows, macOS, and Linux
        - Does NOT use shell - executes directly for security and performance
    """
    if not command:
        raise ValueError("Command list cannot be empty")

    # Get the executable (first argument)
    executable = command[0]
    executable_str = str(executable)

    # Resolve the full path to the executable
    # If it's already an absolute path, check if it exists
    # Otherwise, search in PATH
    executable_path = Path(executable_str)
    if executable_path.is_absolute():
        if not executable_path.exists():
            raise FileNotFoundError(
                f"Executable not found at specified path: {executable_str}"
            )
        resolved_executable = str(executable_path)
    else:
        # Search for the executable in PATH
        resolved_executable = shutil.which(executable_str)
        if resolved_executable is None:
            raise FileNotFoundError(
                f"Executable '{executable_str}' not found in PATH. "
                f"Please ensure it's installed and available in your system PATH."
            )

    # Build the command with resolved executable
    cmd = [resolved_executable] + [str(arg) for arg in command[1:]]

    if sys.platform == "win32":
        # Windows: Use DETACHED_PROCESS to create a process with no console attached
        # and CREATE_NEW_PROCESS_GROUP to prevent Ctrl+C from propagating
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200

        subprocess.Popen(
            cmd,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    else:
        # Unix-like systems: Use start_new_session to create a new session
        # with the process as the session leader, detaching from the terminal
        subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
