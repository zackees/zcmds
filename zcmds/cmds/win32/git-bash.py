# pylint: skip-file
# mypy: ignore-errors

import subprocess

subprocess.Popen(
    r'"C:\Program Files\Git\git-bash.exe"',
    shell=True,
    start_new_session=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE,  # pylint: disable
)
