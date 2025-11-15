"""
Interactive process killer using psutil and prompt_toolkit.

This command provides an interactive interface to browse running processes
and selectively terminate them.
"""

import _thread
import logging
import sys
from typing import List

import psutil
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("snipe.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages process listing and killing operations."""

    def __init__(self) -> None:
        """Initialize the process manager."""
        self.processes: List[psutil.Process] = []
        self.selected_index: int = 0
        self.refresh_processes()

    def refresh_processes(self) -> None:
        """Refresh the list of running processes."""
        try:
            # Request only essential fields that work cross-platform
            self.processes = list(
                psutil.process_iter(["pid", "name"])  # type: ignore[reportUnknownMemberType]
            )
            # Sort by PID
            self.processes.sort(key=lambda p: p.info["pid"])
        except KeyboardInterrupt:
            logger.info("refresh_processes interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error refreshing processes: {e}")
            self.processes = []

    def get_process_list_text(self) -> List[tuple[str, str]]:
        """
        Get formatted text for the process list.

        Returns:
            List of tuples (style, text) for prompt_toolkit.
        """
        try:
            lines: List[tuple[str, str]] = []
            lines.append(("bold", "PID       | User                    | Name\n"))
            lines.append(("", "-" * 80 + "\n"))

            for i, proc in enumerate(self.processes):
                try:
                    pid = proc.info.get("pid", "N/A")
                    name = proc.info.get("name", "N/A")

                    # Try to get username - may fail on some platforms or require privileges
                    username = "N/A"
                    try:
                        username = proc.username()
                    except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                        # AccessDenied: insufficient privileges
                        # NoSuchProcess: process terminated
                        # AttributeError: platform doesn't support username
                        pass
                    except Exception as e:
                        logger.error(f"Error getting username for PID {pid}: {e}")

                    # Truncate long usernames and names
                    if isinstance(username, str) and len(username) > 23:
                        username = username[:20] + "..."
                    if isinstance(name, str) and len(name) > 40:
                        name = name[:37] + "..."

                    line = f"{pid:<9} | {username:<23} | {name}\n"

                    # Highlight selected process
                    if i == self.selected_index:
                        lines.append(("reverse", line))
                    else:
                        lines.append(("", line))
                except KeyboardInterrupt:
                    logger.info("get_process_list_text interrupted by user")
                    _thread.interrupt_main()
                    break
                except Exception as e:
                    logger.error(f"Error formatting process {i}: {e}")
                    continue

            return lines
        except KeyboardInterrupt:
            logger.info("get_process_list_text interrupted by user")
            _thread.interrupt_main()
            return [("", "")]
        except Exception as e:
            logger.error(f"Error in get_process_list_text: {e}")
            return [("", f"Error: {e}\n")]

    def kill_selected_process(self) -> str:
        """
        Kill the currently selected process.

        Returns:
            Status message string.
        """
        try:
            if not self.processes or self.selected_index >= len(self.processes):
                return "No process selected"

            proc = self.processes[self.selected_index]
            pid = proc.info.get("pid")
            name = proc.info.get("name", "Unknown")

            try:
                proc.kill()
                self.refresh_processes()
                return f"Killed process {pid} ({name})"
            except psutil.NoSuchProcess:
                self.refresh_processes()
                return f"Process {pid} no longer exists"
            except psutil.AccessDenied:
                return f"Access denied for process {pid} ({name})"
        except KeyboardInterrupt:
            logger.info("kill_selected_process interrupted by user")
            _thread.interrupt_main()
            return "Operation cancelled"
        except Exception as e:
            logger.error(f"Error killing process: {e}")
            return f"Error: {e}"

    def move_selection(self, delta: int) -> None:
        """
        Move the selection up or down.

        Args:
            delta: Number of positions to move (-1 for up, 1 for down).
        """
        try:
            if self.processes:
                self.selected_index = max(
                    0, min(len(self.processes) - 1, self.selected_index + delta)
                )
        except KeyboardInterrupt:
            logger.info("move_selection interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error moving selection: {e}")


def create_application() -> Application[None]:
    """
    Create the prompt_toolkit application.

    Returns:
        The configured Application instance.
    """
    try:
        manager = ProcessManager()
        status_message: List[str] = [
            "Ready. Use ↑/↓ to select, K to kill, R to refresh, Q to quit"
        ]

        # Key bindings
        kb = KeyBindings()

        @kb.add("q")
        def quit_app(event: object) -> None:
            """Quit the application."""
            try:
                event.app.exit()  # type: ignore
            except KeyboardInterrupt:
                logger.info("quit_app interrupted by user")
                _thread.interrupt_main()
            except Exception as e:
                logger.error(f"Error in quit_app: {e}")

        @kb.add("up")
        def move_up(event: object) -> None:
            """Move selection up."""
            try:
                manager.move_selection(-1)
            except KeyboardInterrupt:
                logger.info("move_up interrupted by user")
                _thread.interrupt_main()
            except Exception as e:
                logger.error(f"Error in move_up: {e}")

        @kb.add("down")
        def move_down(event: object) -> None:
            """Move selection down."""
            try:
                manager.move_selection(1)
            except KeyboardInterrupt:
                logger.info("move_down interrupted by user")
                _thread.interrupt_main()
            except Exception as e:
                logger.error(f"Error in move_down: {e}")

        @kb.add("k")
        def kill_process(event: object) -> None:
            """Kill the selected process."""
            try:
                result = manager.kill_selected_process()
                status_message[0] = result
            except KeyboardInterrupt:
                logger.info("kill_process interrupted by user")
                _thread.interrupt_main()
            except Exception as e:
                logger.error(f"Error in kill_process: {e}")
                status_message[0] = f"Error: {e}"

        @kb.add("r")
        def refresh(event: object) -> None:
            """Refresh the process list."""
            try:
                manager.refresh_processes()
                status_message[0] = "Process list refreshed"
            except KeyboardInterrupt:
                logger.info("refresh interrupted by user")
                _thread.interrupt_main()
            except Exception as e:
                logger.error(f"Error in refresh: {e}")
                status_message[0] = f"Error: {e}"

        # Layout components
        process_list_control = FormattedTextControl(
            text=lambda: manager.get_process_list_text()
        )

        status_bar_control = FormattedTextControl(
            text=lambda: [("reverse", f" {status_message[0]} ")]
        )

        layout = Layout(
            HSplit(
                [
                    Window(
                        content=process_list_control,
                        always_hide_cursor=True,
                    ),
                    Window(
                        content=status_bar_control,
                        height=1,
                    ),
                ]
            )
        )

        # Create application
        app: Application[None] = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=True,
            mouse_support=False,
        )

        return app
    except KeyboardInterrupt:
        logger.info("create_application interrupted by user")
        _thread.interrupt_main()
        raise
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise


def main() -> int:
    """
    Main entry point for the snipe command.

    Interactive process killer using psutil and prompt_toolkit.
    Navigate with arrow keys, kill with 'k', refresh with 'r', quit with 'q'.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        app = create_application()
        app.run()
        return 0
    except KeyboardInterrupt:
        logger.info("snipe command interrupted by user")
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"Error in snipe command: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
