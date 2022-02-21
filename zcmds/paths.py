"""
    Holds paths used by other parts of the system.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CMD_COMMON_DIR = os.path.join(BASE_DIR, "cmds", "common")
CMD_WIN32_DIR = os.path.join(BASE_DIR, "cmds", "win32")
CMD_DARWIN_DIR = os.path.join(BASE_DIR, "cmds", "darwin")
CMD_LINUX_DIR = os.path.join(BASE_DIR, "cmds", "linux")
BIN_DIR = os.path.abspath(os.path.join(BASE_DIR, "bin"))
