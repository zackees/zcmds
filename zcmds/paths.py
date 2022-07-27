"""
    Holds paths used by other parts of the system.
"""

import os

from appdirs import user_data_dir

USER_DIR = user_data_dir("zcmds")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CMD_DIR = os.path.join(PROJECT_ROOT, "cmds")
CMD_COMMON_DIR = os.path.join(CMD_DIR, "common")
CMD_WIN32_DIR = os.path.join(CMD_DIR, "win32")
CMD_DARWIN_DIR = os.path.join(CMD_DIR, "darwin")
CMD_LINUX_DIR = os.path.join(CMD_DIR, "linux")
BIN_DIR = os.path.join(USER_DIR, "bin")
