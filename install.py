import platform
import sys
import os

(major, _, _) = platform.python_version_tuple()
major = int(major)

if major < 3:
    sys.stderr.write("Please use python 3+\n")
    sys.exit(-1)

SELF_DIR = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(SELF_DIR, 'pysrc', 'cmds', 'common'))

print(target_dir)
assert os.path.exists(target_dir), f"platform doesn't exist for {target_dir}"

print("Load platform dependent update and run it's main program.")
sys.path.insert(0, target_dir)
from update import main as platform_main
platform_main()
