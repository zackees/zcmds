# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

zcmds is a cross-platform productivity command-line toolset written in Python. It provides utilities for media manipulation through ffmpeg, AI integration, and common Unix commands on Windows. The project is actively maintained and uses modern Python packaging standards.

## Development Commands

### Essential Commands

```bash
# Linting (MUST run before committing)
./lint  # Runs isort, black, ruff, and mypy

# Testing (MUST run before committing)
./test  # Runs unittest discovery

# Build and Install
./install  # Installs package in development mode
./clean    # Cleans build artifacts

# Package Management
pip install -e .  # Install in development mode
python setup.py sdist bdist_wheel  # Build distribution
./upload_package.sh  # Upload to PyPI
```

### Code Quality Requirements

Before marking any task as complete, you MUST:
1. Run `./lint` and ensure it passes with no errors
2. Run `./test` and ensure all tests pass

Both commands must exit with status code 0.

## Architecture

### Project Structure

- **src/zcmds/**: Main package directory
  - **cmds/**: Command implementations organized by platform
    - **common/**: Cross-platform commands (majority of tools)
    - **darwin/**: macOS-specific commands
    - **linux/**: Linux-specific commands
  - **util/**: Shared utility functions
  - **install/**: Installation-related code
  - **cmds.txt**: Registry of all available commands (entry points)

### Command Registration

New commands are registered in `src/zcmds/cmds.txt` using the format:
```
command_name = "zcmds.cmds.common.module_name:main"
```

The `setup.py` dynamically reads this file to generate console script entry points.

### Key Design Patterns

1. **Platform-specific implementations**: Commands check `sys.platform` and import platform-specific utilities when needed (e.g., `zcmds_win32` for Windows)

2. **FFmpeg integration**: Many video/audio commands use `static-ffmpeg` for cross-platform media processing

3. **AI tool integration**: Commands like `askai` and `aicode` integrate with external AI packages (`advanced-askai`, `advanced-aicode`)

4. **Command structure**: Each command module typically has a `main()` function that serves as the entry point

## Testing Approach

- Unit tests are in the `tests/` directory
- Run tests with `./test` or `python -m unittest discover tests -v`
- Tests use Python's built-in `unittest` framework

## Dependencies

- Python 3.10+ required
- Major dependencies include: ffmpeg tools, PyQt6 for GUI elements, OpenAI API, various media processing libraries
- Windows-specific: `zcmds_win32` package provides Unix-like commands

## Git Workflow

The repository uses:
- Main branch: `master`
- Standard git workflow with pull requests
- Git status/diff commands available through custom tools (`git-diff`, `push`, `pull`)