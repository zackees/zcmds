"""Text editor with line numbers, syntax-aware wrapping, and auto-save."""

import _thread
import ctypes
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
error_file_handler = ErrorFileHandler("editor.err")
error_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(error_file_handler)


class LineNumberedText(tk.Frame):
    """
    Text widget with synchronized line numbers.

    Display Normalization Strategy:
    ================================
    The key challenge is keeping line numbers perfectly synchronized with the text
    widget across all scroll events (mouse wheel, keyboard, scrollbar, text insertion).

    Architecture:
    ------------
    1. SINGLE SOURCE OF TRUTH: Only the main text widget has yscrollcommand
       - The text widget is the "master" that drives all scrolling
       - Line numbers widget is a "slave" that follows the text widget
       - This prevents feedback loops and ensures consistent behavior

    2. SCROLLBAR AS INTERMEDIARY: The scrollbar connects both widgets
       - Text widget reports scroll position → _on_scrollbar_set()
       - _on_scrollbar_set() updates scrollbar AND synchronizes line numbers
       - When user drags scrollbar → _on_scroll() moves both widgets together

    3. FONT MATCHING: Both widgets use identical fonts
       - Ensures line numbers align perfectly with text lines
       - Font size changes update both widgets simultaneously
       - Same font metrics = same line height = perfect alignment

    This architecture eliminates scroll desynchronization issues that plagued
    earlier versions where line numbers would "drift" or lag behind the text.
    """

    def __init__(self, parent: tk.Widget | tk.Tk, **kwargs: Any) -> None:
        # Dark Theme Color Palette
        # ------------------------
        # Consistent dark color scheme for professional code editor look
        self.bg_dark = "#1e1e1e"  # Main background (VS Code dark)
        self.bg_darker = "#252526"  # Line numbers background (slightly darker)
        self.fg_light = "#d4d4d4"  # Main text color (light gray)
        self.fg_dim = "#858585"  # Line numbers color (dimmed)
        self.selection_bg = "#264f78"  # Selection background (blue-gray)
        self.cursor_color = "#aeafad"  # Cursor color (light gray)

        # Initialize frame with dark background
        tk.Frame.__init__(self, parent, bg=self.bg_dark)
        self.parent = parent

        # Debouncing for resize events to prevent excessive redraw during window resize
        self._resize_timer: Optional[str] = None

        # Extract font from kwargs to use for line numbers
        # CRITICAL: Both widgets MUST use the same font for proper line alignment
        # If fonts differ even slightly, line numbers will misalign with text
        text_font = kwargs.get("font", ("Courier", 14))

        # Create line number widget with dark theme colors
        # IMPORTANT: No yscrollcommand set here - this widget is a "follower"
        # It receives scroll commands but doesn't report its scroll position
        # This prevents circular dependencies and keeps scrolling predictable
        self.line_numbers = tk.Text(
            self,
            width=4,  # Wide enough for 4-digit line numbers
            padx=4,
            takefocus=0,  # Don't steal focus from main text
            border=0,
            background=self.bg_darker,  # Darker shade for line numbers
            foreground=self.fg_dim,  # Dimmed text for line numbers
            state="disabled",  # Read-only - prevents user editing
            wrap="none",  # Line numbers never wrap
            font=text_font,  # MUST match main text font for alignment
        )
        self.line_numbers.pack(side="left", fill="y")

        # Create main text widget with dark theme
        # This is the "master" widget that drives all scrolling behavior
        # yscrollcommand=_on_scrollbar_set is the KEY to synchronization:
        # - Every time this widget scrolls (by ANY means), it calls _on_scrollbar_set
        # - _on_scrollbar_set then synchronizes the line numbers to match

        # Remove background and foreground from kwargs if present (we'll set our own)
        text_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k
            not in [
                "background",
                "foreground",
                "bg",
                "fg",
                "insertbackground",
                "selectbackground",
                "selectforeground",
            ]
        }

        self.text = tk.Text(
            self,
            **text_kwargs,
            yscrollcommand=self._on_scrollbar_set,  # type: ignore[arg-type]
            background=self.bg_dark,  # Dark background
            foreground=self.fg_light,  # Light text
            insertbackground=self.cursor_color,  # Cursor color
            selectbackground=self.selection_bg,  # Selection background
            selectforeground=self.fg_light,  # Selection text color
        )
        self.text.pack(side="left", fill="both", expand=True)

        # Create scrollbar that controls both widgets
        # command=_on_scroll ensures user dragging scrollbar moves both widgets
        self.scrollbar = tk.Scrollbar(self, command=self._on_scroll)
        self.scrollbar.pack(side="right", fill="y")

        # Bind events for line number updates
        # These ensure line number count updates when text is added/removed
        self.text.bind(
            "<<Change>>", self._on_change
        )  # Virtual event for content changes
        self.text.bind("<Configure>", self._on_configure)  # Window resize events
        self.text.bind("<KeyRelease>", self._on_change)  # After typing

        # Bind mouse wheel events for synchronized scrolling
        # Why bind to both widgets? So scrolling works when hovering over either one
        # Both handlers call the same method to ensure identical behavior
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.line_numbers.bind("<MouseWheel>", self._on_mousewheel)

        # Bind additional scrolling events to ensure line numbers stay synchronized
        # These catch edge cases where yscrollcommand might not fire immediately
        # add=True preserves existing bindings (doesn't replace them)
        self.text.bind(
            "<KeyPress>", self._on_text_scroll, add=True
        )  # Arrow keys, Page Up/Down
        self.text.bind(
            "<Button-1>", self._on_text_scroll, add=True
        )  # Mouse click (may scroll to cursor)

        # Initial update to populate line numbers on startup
        self._update_line_numbers()

    def _on_change(self, event: Optional[tk.Event] = None) -> str:
        """
        Handle text changes to update line numbers.

        Called when: User types, deletes, or modifies text content

        Updates line number count when lines are added/removed.
        Returns "break" to prevent event propagation.
        """
        self._update_line_numbers()
        return "break"

    def _on_configure(self, event: Optional[tk.Event] = None) -> str:
        """
        Handle configure events (including resize) with debouncing.

        Called when: Window is resized, moved, or reconfigured

        Debouncing strategy:
        - Window resize can fire MANY configure events rapidly
        - We don't want to redraw line numbers hundreds of times per second
        - Instead: cancel pending update, schedule new one 100ms later
        - Result: Only redraw once after resize settles

        This prevents performance issues during window resize operations.
        """
        # Cancel previous scheduled update (if any)
        if self._resize_timer is not None:
            self.after_cancel(self._resize_timer)

        # Schedule update after 100ms of inactivity
        # If another configure event fires within 100ms, we'll cancel and reschedule
        self._resize_timer = self.after(100, self._update_line_numbers)
        return "break"

    def _update_line_numbers(self) -> None:
        """
        Update the line numbers display to match current text content.

        Called by:
        - _on_change: when text content changes
        - _on_configure: when window is resized (debounced)
        - __init__: initial population

        Process:
        1. Calculate total number of lines in text widget
        2. Generate string "1\n2\n3\n..." up to line count
        3. Replace entire line number widget content

        Note: Line numbers widget is normally disabled (read-only).
        We temporarily enable it to update content, then disable again.
        """
        self._resize_timer = None

        # Get total line count from text widget
        # text.index("end-1c") returns position of last character
        # Format is "line.column", we extract the line number
        line_numbers_content = "\n".join(
            str(i) for i in range(1, int(self.text.index("end-1c").split(".")[0]) + 1)
        )

        # Update line numbers (must enable, edit, then disable again)
        self.line_numbers.config(state="normal")  # Enable editing
        self.line_numbers.delete("1.0", "end")  # Clear existing content
        self.line_numbers.insert("1.0", line_numbers_content)  # Insert new numbers
        self.line_numbers.config(state="disabled")  # Disable editing (read-only)

    def _on_scroll(self, *args: Any) -> None:
        """
        Handle scrollbar drag events - update both text widgets.

        Called when: User drags the scrollbar thumb

        Flow:
        1. User drags scrollbar
        2. Scrollbar calls this method with scroll command (e.g., "moveto", 0.5)
        3. We apply the command to BOTH text and line_numbers widgets
        4. Both widgets scroll in perfect sync

        Note: We must update both explicitly because line_numbers has no yscrollcommand
        """
        self.text.yview(*args)  # type: ignore[no-untyped-call]
        self.line_numbers.yview(*args)  # type: ignore[no-untyped-call]

    def _on_scrollbar_set(self, first: str, last: str) -> None:
        """
        Update scrollbar and synchronize line numbers with text widget.

        Called when: Text widget scrolls (by ANY means: typing, arrow keys, mouse wheel, etc.)

        This is the HEART of the synchronization system:
        - The text widget has yscrollcommand=self._on_scrollbar_set
        - Every time text scrolls, Tk calls this with the new visible range
        - first: fraction of document visible at top (0.0 = start, 1.0 = end)
        - last: fraction of document visible at bottom

        Flow:
        1. Text widget scrolls (user types, presses arrow key, uses mouse wheel, etc.)
        2. Tk automatically calls _on_scrollbar_set with new position
        3. We update scrollbar thumb to reflect new position
        4. We synchronize line numbers to match text position

        Why this works:
        - Text widget is the single source of truth
        - Line numbers are always kept in sync with text
        - No circular dependencies (line_numbers doesn't have yscrollcommand)
        """
        # Update scrollbar position
        self.scrollbar.set(first, last)  # type: ignore[arg-type]

        # Synchronize line numbers with text widget position
        # Use yview_moveto to set absolute position (not relative scroll)
        self.line_numbers.yview_moveto(float(first))  # type: ignore[no-untyped-call]

    def _on_text_scroll(self, event: Optional[tk.Event] = None) -> None:
        """
        Ensure line numbers stay synchronized after any text widget scroll.

        Called when: Keyboard navigation or mouse clicks in text widget

        Why needed: Some scroll events (arrow keys, Page Up/Down, mouse clicks)
        might not immediately trigger yscrollcommand. We schedule a sync to catch
        these edge cases.

        The 1ms delay ensures the text widget has finished its internal scroll
        operations before we read its position.
        """
        # Schedule sync after a short delay to let the text widget finish scrolling
        self.after(1, self._sync_line_numbers_scroll)

    def _sync_line_numbers_scroll(self) -> None:
        """
        Synchronize line numbers with current text widget scroll position.

        Called by: _on_text_scroll (after 1ms delay)

        This is a "catch-all" synchronization that reads the text widget's current
        scroll position and forces line numbers to match it. Used for edge cases
        where the normal yscrollcommand path might not have fired yet.
        """
        # Get current scroll position of text widget
        # yview() returns tuple: (top_fraction, bottom_fraction)
        yview = self.text.yview()  # type: ignore[no-untyped-call]
        # Update line numbers to match - use first element (top position)
        self.line_numbers.yview_moveto(yview[0])  # type: ignore[no-untyped-call]

    def _on_mousewheel(self, event: tk.Event) -> str:
        """
        Handle mouse wheel scrolling for synchronized movement.

        Called when: User scrolls mouse wheel over text OR line numbers

        Why needed: Mouse wheel events need special handling:
        1. They might not trigger yscrollcommand immediately
        2. We want consistent behavior regardless of which widget is hovered
        3. Different platforms report delta differently

        Platform differences:
        - Windows: event.delta is in multiples of 120 (one "click" = 120)
        - macOS/Linux: event.delta is typically ±1

        We manually scroll both widgets to ensure perfect synchronization.
        """
        # Calculate scroll amount (Windows uses delta/120, others use delta)
        if sys.platform == "win32":
            delta = -1 * (event.delta // 120)
        else:
            delta = -1 * event.delta

        # Scroll both widgets by the same amount
        # Using yview_scroll with "units" scrolls by lines
        self.text.yview_scroll(delta, "units")
        self.line_numbers.yview_scroll(delta, "units")

        # Return "break" to prevent event propagation (stops default behavior)
        return "break"


class Editor:
    """
    Main editor application for text files.

    Display Normalization Architecture:
    ===================================
    This editor achieves proper display across different DPI settings and ensures
    perfect synchronization between text content and line numbers.

    Three Key Components:
    ---------------------

    1. DPI SCALING (_setup_dpi_scaling):
       - Sets Windows process as DPI-aware (per-monitor mode)
       - Tk automatically detects monitor DPI and calculates scaling
       - We use base font sizes (14pt) - Tk scales them automatically
       - No manual scaling needed - prevents double-scaling issues
       - Works across multi-monitor setups with different DPI

    2. FONT SYNCHRONIZATION (_create_widgets, _change_font_size):
       - Both text widget and line numbers use IDENTICAL fonts
       - Same font family, same size, same metrics = perfect line alignment
       - Font changes update BOTH widgets simultaneously
       - This prevents line number "drift" or misalignment

    3. SCROLL SYNCHRONIZATION (LineNumberedText class):
       - Text widget is the "master" with yscrollcommand
       - Line numbers widget is the "slave" that follows
       - _on_scrollbar_set intercepts all scroll events and syncs line numbers
       - Multiple event handlers catch edge cases (mouse wheel, keyboard, etc.)
       - Result: Line numbers stay perfectly aligned regardless of scroll method

    Together, these systems ensure:
    - Crisp, properly sized text on HiDPI displays
    - Perfect line number alignment at all font sizes
    - Synchronized scrolling in all scenarios
    - Consistent behavior across platforms
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.root = tk.Tk()

        # Dark Theme Color Palette
        # ------------------------
        # Consistent dark color scheme matching the text editor
        self.bg_dark = "#1e1e1e"  # Main background
        self.bg_darker = "#252526"  # Darker elements
        self.fg_light = "#d4d4d4"  # Light text
        self.fg_dim = "#858585"  # Dimmed text
        self.status_bg = "#007acc"  # Status bar background (VS Code blue)
        self.status_fg = "#ffffff"  # Status bar text (white)

        # Set up DPI scaling for HiDPI displays
        self._setup_dpi_scaling()

        self.root.title(f"Editor - {file_path}")

        # Apply dark theme to root window
        self.root.configure(bg=self.bg_dark)

        # Center window on mouse cursor location
        window_width = 800
        window_height = 600
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        # Position window so mouse is at center
        x = mouse_x - window_width // 2
        y = mouse_y - window_height // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Track unsaved changes
        self.dirty = False
        self.auto_save_timer: Optional[Timer] = None

        # Track file modification time for external change detection
        self.last_mtime: Optional[float] = None

        # Font settings - use base font size (Tk auto-scales based on DPI)
        # Display Normalization: Font Management
        # ---------------------------------------
        # We store a base font size (e.g., 14pt) that Tk automatically scales
        # based on the monitor's DPI. On a 175% scaled display (168 DPI),
        # Tk's scaling factor is ~2.33×, so 14pt becomes 33 pixels.
        # Both text widget and line numbers use this SAME font to maintain alignment.
        self.current_font_size = 14
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

    def _setup_dpi_scaling(self) -> None:
        """
        Configure DPI scaling for HiDPI displays across all platforms.

        The key insight: Once we set DPI awareness, Tk automatically calculates
        the correct scaling factor based on the monitor's DPI. We should NOT
        manually override this with tk.call("tk", "scaling", ...) or manually
        scale font sizes, as this causes double-scaling.

        How it works:
        1. Call SetProcessDpiAwareness(2) on Windows (per-monitor DPI aware)
        2. Tk detects the DPI and automatically sets scaling (e.g., 2.33× at 168 DPI)
        3. Use base font sizes (e.g., 14pt) - Tk scales them automatically
        4. Result: 14pt × 2.33 = 33 pixels (perfect for 175% Windows scaling)

        For multi-monitor setups with different DPI (225%, 150%, 175%), mode 2
        ensures the app re-scales when moved between monitors.

        We keep self.dpi_scale = 1.0 (no manual scaling) since Tk handles it all.
        """
        # No manual scaling needed - Tk handles it automatically once DPI-aware
        self.dpi_scale = 1.0

        try:
            if sys.platform == "win32":
                # Windows: Set per-monitor DPI awareness (mode 2)
                # Mode 0 = Unaware, Mode 1 = System aware, Mode 2 = Per-monitor aware
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(2)
                except Exception:
                    # Fall back to older API (Windows Vista+)
                    try:
                        ctypes.windll.user32.SetProcessDPIAware()
                    except Exception:
                        pass

                # That's it! Tk will automatically detect DPI and scale everything.
                # No need to manually call tk.call("tk", "scaling", ...)

            elif sys.platform == "darwin":
                # macOS: Tk handles Retina displays automatically
                # No manual intervention needed
                pass

            else:
                # Linux: Tk should respect the system DPI settings
                # If not working, users can set GDK_SCALE environment variable
                pass

        except KeyboardInterrupt:
            logger.info("_setup_dpi_scaling interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            # Don't let DPI scaling errors prevent the editor from starting
            logger.error(f"Error setting up DPI scaling: {e}")
            self.dpi_scale = 1.0

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
        """
        Create all GUI widgets.

        Display Normalization: Widget Creation
        ---------------------------------------
        The font parameter passed to LineNumberedText is CRITICAL:
        - LineNumberedText extracts this font in __init__
        - It applies the SAME font to both text and line_numbers widgets
        - This ensures identical line heights and perfect alignment
        - Any font size changes must update BOTH widgets (see _change_font_size)
        """
        # Create menu bar
        self._create_menu_bar()

        # Create text editor with line numbers
        # The font parameter is extracted by LineNumberedText and used for both widgets
        self.text_frame = LineNumberedText(
            self.root,
            wrap=self.wrap_mode,
            undo=True,
            maxundo=-1,
            font=(
                self.font_family,
                self.current_font_size,
            ),  # Shared font for both widgets
        )
        self.text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Track text changes
        self.text_frame.text.bind("<<Modified>>", self._on_text_modified)

        # Status bar with dark theme
        # Using ttk.Label with custom style for dark theme
        style = ttk.Style()
        style.configure(
            "Dark.TLabel",
            background=self.status_bg,
            foreground=self.status_fg,
            relief=tk.FLAT,
            padding=(5, 2),
        )
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            style="Dark.TLabel",
            anchor="w",
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _create_menu_bar(self) -> None:
        """Create the menu bar with options (dark themed)."""
        try:
            # Use readable font size for menus (scaled by DPI)
            # Increased from 9 to 11 for better readability
            menu_font = tkfont.Font(family="Segoe UI", size=11)

            # Create menu bar with dark theme
            # Note: Add relief and borderwidth for better dark mode appearance
            menubar = tk.Menu(
                self.root,
                font=menu_font,
                bg=self.bg_darker,
                fg=self.fg_light,
                activebackground=self.status_bg,
                activeforeground=self.status_fg,
                borderwidth=0,
                relief=tk.FLAT,
            )
            self.root.config(menu=menubar)

            # File menu with dark theme
            # Include all color properties for complete dark mode coverage
            file_menu = tk.Menu(
                menubar,
                tearoff=0,
                font=menu_font,
                bg=self.bg_darker,
                fg=self.fg_light,
                activebackground=self.status_bg,
                activeforeground=self.status_fg,
                selectcolor=self.fg_light,  # Checkmark color
                disabledforeground=self.fg_dim,  # Disabled items
                borderwidth=1,
                relief=tk.FLAT,
            )
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(
                label="Save", command=self._save_file, accelerator="Ctrl+S"
            )
            file_menu.add_separator()
            file_menu.add_command(
                label="Exit", command=self._on_closing, accelerator="Ctrl+Q"
            )

            # View menu with dark theme
            # Include all color properties for complete dark mode coverage
            view_menu = tk.Menu(
                menubar,
                tearoff=0,
                font=menu_font,
                bg=self.bg_darker,
                fg=self.fg_light,
                activebackground=self.status_bg,
                activeforeground=self.status_fg,
                selectcolor=self.fg_light,  # Checkmark color
                disabledforeground=self.fg_dim,  # Disabled items
                borderwidth=1,
                relief=tk.FLAT,
            )
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

            # Font size controls via menu items and keyboard shortcuts
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

        # Ctrl+MouseWheel for font size control
        self.text_frame.text.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        self.text_frame.line_numbers.bind(
            "<Control-MouseWheel>", self._on_ctrl_mousewheel
        )

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
        """
        Change the font size by a delta amount.

        Called by: Keyboard shortcuts (Ctrl+Plus/Ctrl+Minus) and menu items

        Font Normalization:
        ------------------
        Same principle as _on_font_size_change: both widgets must share the same font.
        Delta changes (increment/decrement by 1) are applied to current size.

        Args:
            delta: Amount to change font size (+1 to increase, -1 to decrease)
        """
        try:
            self.current_font_size += delta
            self.current_font_size = max(8, min(32, self.current_font_size))

            new_font = tkfont.Font(family=self.font_family, size=self.current_font_size)

            # Update both main text and line numbers with identical font
            # This ensures line numbers stay perfectly aligned with text
            self.text_frame.text.config(font=new_font)
            self.text_frame.line_numbers.config(font=new_font)

            self.status_bar.config(text=f"Font size: {self.current_font_size}")

        except KeyboardInterrupt:
            logger.info("_change_font_size interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error changing font size: {e}")

    def _on_ctrl_mousewheel(self, event: tk.Event) -> str:
        """
        Handle Ctrl+MouseWheel events to change font size.

        Called when: User scrolls mouse wheel while holding Ctrl key

        This provides a smooth way to adjust font size using the mouse wheel:
        - Ctrl+MouseWheel Up: Increase font size
        - Ctrl+MouseWheel Down: Decrease font size

        Platform differences:
        - Windows: event.delta is in multiples of 120 (one "click" = 120)
        - macOS/Linux: event.delta is typically ±1

        Args:
            event: Mouse wheel event with delta information

        Returns:
            "break" to prevent event propagation
        """
        try:
            # Calculate delta direction (positive = wheel up = increase font)
            if sys.platform == "win32":
                delta = 1 if event.delta > 0 else -1
            else:
                delta = 1 if event.delta > 0 else -1

            # Change font size
            self._change_font_size(delta)

        except KeyboardInterrupt:
            logger.info("_on_ctrl_mousewheel interrupted by user")
            _thread.interrupt_main()
        except Exception as e:
            logger.error(f"Error handling Ctrl+MouseWheel: {e}")

        # Return "break" to prevent default scrolling behavior
        return "break"

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

            # Print the saved filename to stdout for user visibility
            print(str(self.file_path))

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
