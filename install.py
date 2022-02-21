import platform
import sys
import os

from zcmds.install.update import main as platform_main

(major, _, _) = platform.python_version_tuple()
major = int(major)

if major < 3:
    sys.stderr.write("Please use python 3+\n")
    sys.exit(-1)

platform_main()
