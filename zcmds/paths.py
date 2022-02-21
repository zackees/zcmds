"""
    Holds paths used by other parts of the system.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CMD_COMMON_DIR = os.path.join(BASE_DIR, "cmds", "common")
BIN_DIR = os.path.abspath(os.path.join(BASE_DIR, "bin"))
