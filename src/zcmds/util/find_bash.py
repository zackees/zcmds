import shutil
from pathlib import Path


def find_bash() -> Path | Exception:
    """Finds the bash executable."""
    bash = Path("/bin/bash")
    if bash.exists():
        return bash

    bash = Path("/usr/bin/bash")
    if bash.exists():
        return bash

    bash = Path("C:\\Program Files\\Git\\bin\\bash.exe")
    if bash.exists():
        return bash
    bash = Path("C:\\Program Files\\Git\\usr\\bin\\bash.exe")
    if bash.exists():
        return bash
    bash = Path("C:\\Program Files\\Git\\bash.exe")
    if bash.exists():
        return bash
    bash = Path("C:\\Program Files\\Git\\usr\\bash.exe")
    if bash.exists():
        return bash
    maybe_bash = shutil.which("bash")
    if maybe_bash:
        return Path(maybe_bash)
    raise Exception("Bash not found")
