"""
    Holds paths used by other parts of the system.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CMD_DIR = os.path.join(BASE_DIR, "cmds")
CMD_COMMON_DIR = os.path.join(CMD_DIR, "common")
CMD_WIN32_DIR = os.path.join(CMD_DIR, "win32")
CMD_DARWIN_DIR = os.path.join(CMD_DIR, "darwin")
CMD_LINUX_DIR = os.path.join(CMD_DIR, "linux")
BIN_DIR = os.path.join(BASE_DIR, "bin")
