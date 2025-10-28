"""Task notepad editor - opens ~/Desktop/task.md or ~/task.md in a tkinter editor."""

import _thread
import logging
import signal
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from threading import Timer
from tkinter import font as tkfont
from tkinter import ttk
from typing import Any, Optional


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


class LineNumberedText(tk.Frame):
    """Text widget with line numbers."""

    def __init__(self, parent: tk.Widget | tk.Tk, **kwargs: Any) -> None:
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Debouncing for resize events
        self._resize_timer: Optional[str] = None

        # Create line number widget
        self.line_numbers = tk.Text(
            self,
            width=4,
            padx=4,
            takefocus=0,
            border=0,
            background="#f0f0f0",
            state="disabled",
            wrap="none",
            yscrollcommand=self._on_scrollbar_set,  # type: ignore[arg-type]
        )
        self.line_numbers.pack(side="left", fill="y")

        # Create main text widget
        self.text = tk.Text(self, **kwargs, yscrollcommand=self._on_scrollbar_set)  # type: ignore[arg-type]
        self.text.pack(side="left", fill="both", expand=True)

        # Create scrollbar that controls both widgets
        self.scrollbar = tk.Scrollbar(self, command=self._on_scroll)
        self.scrollbar.pack(side="right", fill="y")

        # Bind events for line number updates
        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_configure)
        self.text.bind("<KeyRelease>", self._on_change)

        # Bind mouse wheel events for synchronized scrolling
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.line_numbers.bind("<MouseWheel>", self._on_mousewheel)

        # Initial update
        self._update_line_numbers()

    def _on_change(self, event: Optional[tk.Event] = None) -> str:
        """Handle text changes to update line numbers."""
        self._update_line_numbers()
        return "break"

    def _on_configure(self, event: Optional[tk.Event] = None) -> str:
        """Handle configure events (including resize) with debouncing."""
        # Cancel previous scheduled update
        if self._resize_timer is not None:
            self.after_cancel(self._resize_timer)

        # Schedule update after 100ms of inactivity
        self._resize_timer = self.after(100, self._update_line_numbers)
        return "break"

    def _update_line_numbers(self) -> None:
        """Update the line numbers display."""
        self._resize_timer = None
        line_numbers_content = "\n".join(
            str(i) for i in range(1, int(self.text.index("end-1c").split(".")[0]) + 1)
        )

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers_content)
        self.line_numbers.config(state="disabled")

    def _on_scroll(self, *args: Any) -> None:
        """Handle scrollbar movement - update both text widgets."""
        self.text.yview(*args)  # type: ignore[no-untyped-call]
        self.line_numbers.yview(*args)  # type: ignore[no-untyped-call]

    def _on_scrollbar_set(self, first: str, last: str) -> None:
        """Update scrollbar and synchronize both widgets."""
        # Update scrollbar
        self.scrollbar.set(first, last)  # type: ignore[arg-type]

        # Synchronize line numbers with text widget
        self.line_numbers.yview_moveto(float(first))  # type: ignore[no-untyped-call]

    def _on_mousewheel(self, event: tk.Event) -> str:
        """Handle mouse wheel scrolling for synchronized movement."""
        # Calculate scroll amount (Windows uses delta/120, others use delta)
        if sys.platform == "win32":
            delta = -1 * (event.delta // 120)
        else:
            delta = -1 * event.delta

        # Scroll both widgets
        self.text.yview_scroll(delta, "units")
        self.line_numbers.yview_scroll(delta, "units")

        return "break"


class TaskEditor:
    """Main task editor application."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.root = tk.Tk()
        self.root.title(f"Task Editor - {file_path}")
        self.root.geometry("800x600")

        # Track unsaved changes
        self.dirty = False
        self.auto_save_timer: Optional[Timer] = None

        # Track file modification time for external change detection
        self.last_mtime: Optional[float] = None

        # Font settings
        self.current_font_size = 11
        self.font_family = "Consolas" if sys.platform == "win32" else "Courier"

        # Determine wrap mode based on file type
        self.wrap_mode = self._determine_wrap_mode(file_path)

        self._create_widgets()
        self._bind_shortcuts()
        self._load_file()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Set up signal handler for Ctrl-C (SIGINT)
        signal.signal(signal.SIGINT, self._handle_interrupt)

        # Start file monitoring
        self._schedule_file_check()

    def _determine_wrap_mode(self, file_path: Path) -> str:
        """
        Determine whether to enable line wrapping based on file type.

        Returns:
            "word" for text/markdown files, "none" for code files
        """
        # Extensions that should have word wrap enabled
        wrap_extensions = {
            ".txt",
            ".md",
            ".markdown",
            ".rst",
            ".tex",
            ".log",
        }

        # Extensions that should NOT have word wrap (source code files)
        no_wrap_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".c",
            ".cpp",
            ".cc",
            ".cxx",
            ".h",
            ".hpp",
            ".hh",
            ".hxx",
            ".java",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".kts",
            ".scala",
            ".pl",
            ".lua",
            ".vim",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
            ".ps1",
            ".bat",
            ".cmd",
            ".html",
            ".htm",
            ".xml",
            ".css",
            ".scss",
            ".less",
            ".sass",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            ".sql",
            ".r",
            ".m",
            ".cs",
            ".vb",
            ".fs",
            ".clj",
            ".cljs",
            ".lisp",
            ".scm",
            ".el",
            ".erl",
            ".ex",
            ".exs",
            ".dart",
            ".jl",
            ".zig",
            ".v",
        }

        suffix = file_path.suffix.lower()

        # Check for explicit wrap extensions first
        if suffix in wrap_extensions:
            return "word"

        # Check for no-wrap extensions
        if suffix in no_wrap_extensions:
            return "none"

        # Default to word wrap for unknown extensions
        return "word"

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Create menu bar
        self._create_menu_bar()

        # Create text editor with line numbers
        self.text_frame = LineNumberedText(
            self.root,
            wrap=self.wrap_mode,
            undo=True,
            maxundo=-1,
            font=(self.font_family, self.current_font_size),
        )
        self.text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Track text changes
        self.text_frame.text.bind("<<Modified>>", self._on_text_modified)

        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor="w",
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _create_menu_bar(self) -> None:
        """Create the menu bar with options."""
        try:
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)

            # File menu
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(
                label="Save", command=self._save_file, accelerator="Ctrl+S"
            )
            file_menu.add_separator()
            file_menu.add_command(
                label="Exit", command=self._on_closing, accelerator="Ctrl+Q"
            )

            # View menu
            view_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="View", menu=view_menu)

            # Word wrap submenu
            self.word_wrap_var = tk.BooleanVar(value=(self.wrap_mode == "word"))
            view_menu.add_checkbutton(
                label="Word Wrap",
                variable=self.word_wrap_var,
                command=self._toggle_wrap_menu,
                accelerator="Ctrl+W",
            )

            view_menu.add_separator()

            # Font size controls
            font_frame = tk.Frame(view_menu)
            font_label = tk.Label(font_frame, text="Font Size: ")
            font_label.pack(side="left", padx=5)

            # Font size spinbox
            self.font_size_var = tk.IntVar(value=self.current_font_size)
            font_spinbox = tk.Spinbox(
                font_frame,
                from_=8,
                to=32,
                width=5,
                textvariable=self.font_size_var,
                command=self._on_font_size_change,
            )
            font_spinbox.pack(side="left")

            # Bind Enter key to apply font size
            font_spinbox.bind("<Return>", lambda e: self._on_font_size_change())

            view_menu.add_command(
                label="Increase Font",
                command=lambda: self._change_font_size(1),
                accelerator="Ctrl++",
            )
            view_menu.add_command(
                label="Decrease Font",
                command=lambda: self._change_font_size(-1),
                accelerator="Ctrl+-",
            )

        except KeyboardInterrupt:
            logger.info("_create_menu_bar interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error creating menu bar: {e}")

    def _toggle_wrap_menu(self) -> None:
        """Toggle word wrap from menu."""
        try:
            if self.word_wrap_var.get():
                self.wrap_mode = "word"
                wrap_status = "enabled"
            else:
                self.wrap_mode = "none"
                wrap_status = "disabled"

            self.text_frame.text.config(wrap=self.wrap_mode)
            self.status_bar.config(text=f"Line wrapping {wrap_status}")

        except KeyboardInterrupt:
            logger.info("_toggle_wrap_menu interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error toggling wrap: {e}")

    def _on_font_size_change(self) -> None:
        """Handle font size change from spinbox."""
        try:
            new_size = self.font_size_var.get()
            new_size = max(8, min(32, new_size))  # Clamp between 8-32

            self.current_font_size = new_size
            self.font_size_var.set(new_size)

            new_font = tkfont.Font(family=self.font_family, size=self.current_font_size)
            self.text_frame.text.config(font=new_font)

            self.status_bar.config(text=f"Font size: {self.current_font_size}")

        except KeyboardInterrupt:
            logger.info("_on_font_size_change interrupted by user")
            _thread.interrupt_main()
        except (ValueError, tk.TclError):
            # Invalid input, reset to current size
            self.font_size_var.set(self.current_font_size)
        except Exception as e:
            logger.error(f"Error changing font size: {e}")

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        # Save shortcut
        self.root.bind("<Control-s>", lambda e: self._save_file())

        # Quit shortcut
        self.root.bind("<Control-q>", lambda e: self._on_closing())

        # Font size shortcuts
        self.root.bind("<Control-plus>", lambda e: self._change_font_size(1))
        self.root.bind("<Control-equal>", lambda e: self._change_font_size(1))
        self.root.bind("<Control-minus>", lambda e: self._change_font_size(-1))

        # Toggle line wrapping
        self.root.bind("<Control-w>", lambda e: self._toggle_wrap())

        # Undo/Redo are built into the Text widget
        # Ctrl+Z for undo, Ctrl+Y for redo work automatically

    def _on_text_modified(self, event: Optional[tk.Event] = None) -> None:
        """Handle text modification events."""
        if self.text_frame.text.edit_modified():
            self.dirty = True
            self.text_frame.text.edit_modified(False)

            # Reset auto-save timer
            if self.auto_save_timer:
                self.auto_save_timer.cancel()

            self.auto_save_timer = Timer(30.0, self._auto_save)
            self.auto_save_timer.start()

    def _auto_save(self) -> None:
        """Automatically save the file."""
        if self.dirty:
            self._save_file(auto=True)

    def _save_file(self, auto: bool = False) -> None:
        """Save the file to disk."""
        try:
            content = self.text_frame.text.get("1.0", "end-1c")
            self.file_path.write_text(content, encoding="utf-8")
            self.dirty = False

            # Update last modification time after save
            self.last_mtime = self.file_path.stat().st_mtime

            # Update status bar
            timestamp = datetime.now().strftime("%H:%M:%S")
            save_type = "Auto-saved" if auto else "Saved"
            self.status_bar.config(text=f"{save_type} at {timestamp}")

        except KeyboardInterrupt:
            logger.info("_save_file interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            self.status_bar.config(text=f"Error saving: {e}")

    def _load_file(self) -> None:
        """Load the file content into the editor."""
        try:
            if self.file_path.exists():
                content = self.file_path.read_text(encoding="utf-8")
                self.text_frame.text.delete("1.0", "end")
                self.text_frame.text.insert("1.0", content)
                self.text_frame.text.edit_modified(False)
                self.dirty = False

                # Update last modification time
                self.last_mtime = self.file_path.stat().st_mtime

                self.status_bar.config(text=f"Loaded {self.file_path}")
            else:
                # Create empty file
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                self.file_path.write_text("", encoding="utf-8")
                self.last_mtime = self.file_path.stat().st_mtime
                self.status_bar.config(text=f"Created new file: {self.file_path}")

        except KeyboardInterrupt:
            logger.info("_load_file interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            self.status_bar.config(text=f"Error loading: {e}")

    def _change_font_size(self, delta: int) -> None:
        """Change the font size."""
        try:
            self.current_font_size += delta
            self.current_font_size = max(8, min(32, self.current_font_size))

            new_font = tkfont.Font(family=self.font_family, size=self.current_font_size)
            self.text_frame.text.config(font=new_font)

            self.status_bar.config(text=f"Font size: {self.current_font_size}")

        except KeyboardInterrupt:
            logger.info("_change_font_size interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error changing font size: {e}")

    def _toggle_wrap(self) -> None:
        """Toggle line wrapping mode."""
        try:
            # Toggle between "word" and "none"
            if self.wrap_mode == "word":
                self.wrap_mode = "none"
                wrap_status = "disabled"
                self.word_wrap_var.set(False)
            else:
                self.wrap_mode = "word"
                wrap_status = "enabled"
                self.word_wrap_var.set(True)

            self.text_frame.text.config(wrap=self.wrap_mode)
            self.status_bar.config(text=f"Line wrapping {wrap_status}")

        except KeyboardInterrupt:
            logger.info("_toggle_wrap interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error toggling wrap: {e}")

    def _check_file_changes(self) -> None:
        """Check if the file has been modified externally."""
        try:
            if not self.file_path.exists():
                return

            current_mtime = self.file_path.stat().st_mtime

            # If file was modified externally
            if self.last_mtime is not None and current_mtime != self.last_mtime:
                # Only reload if there are no unsaved changes
                if not self.dirty:
                    # Store cursor position
                    cursor_pos = self.text_frame.text.index(tk.INSERT)

                    # Reload file
                    content = self.file_path.read_text(encoding="utf-8")
                    self.text_frame.text.delete("1.0", "end")
                    self.text_frame.text.insert("1.0", content)
                    self.text_frame.text.edit_modified(False)

                    # Restore cursor position if possible
                    try:
                        self.text_frame.text.mark_set(tk.INSERT, cursor_pos)
                        self.text_frame.text.see(tk.INSERT)
                    except tk.TclError:
                        pass

                    self.last_mtime = current_mtime
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.status_bar.config(
                        text=f"Reloaded (external change) at {timestamp}"
                    )
                else:
                    # File changed but we have unsaved changes
                    self.status_bar.config(
                        text="Warning: File modified externally (unsaved changes prevent reload)"
                    )

        except KeyboardInterrupt:
            logger.info("_check_file_changes interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error checking file changes: {e}")

    def _schedule_file_check(self) -> None:
        """Schedule periodic file change checks."""
        try:
            self._check_file_changes()
            # Check again in 1 second
            self.root.after(1000, self._schedule_file_check)
        except KeyboardInterrupt:
            logger.info("_schedule_file_check interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error in file check schedule: {e}")

    def _on_closing(self) -> None:
        """Handle window close event."""
        try:
            # Cancel auto-save timer
            if self.auto_save_timer:
                self.auto_save_timer.cancel()

            # Save if there are unsaved changes
            if self.dirty:
                self._save_file()

            self.root.destroy()

        except KeyboardInterrupt:
            logger.info("_on_closing interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error closing window: {e}")
            self.root.destroy()

    def _handle_interrupt(self, signum: int, frame: Any) -> None:
        """Handle SIGINT (Ctrl-C) signal by gracefully closing the GUI."""
        try:
            logger.info("Received interrupt signal (Ctrl-C), closing gracefully")
            # Schedule the close operation on the tkinter main thread
            # This is safe because tkinter operations must be on the main thread
            self.root.after(0, self._on_closing)
        except Exception as e:
            logger.error(f"Error handling interrupt: {e}")
            # Force quit if graceful close fails
            try:
                self.root.quit()
            except Exception:
                pass

    def run(self) -> None:
        """Start the GUI main loop."""
        self.root.mainloop()


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
        editor = TaskEditor(task_file)
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
