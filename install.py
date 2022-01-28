import platform
import sys
import os

(major, _, _) = platform.python_version_tuple()
major = int(major)

# sys.exit(0)
if major < 3:
    sys.stderr.write("Please use python 3+\n")
    sys.exit(-1)

SELF_DIR = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(SELF_DIR, 'pysrc', 'cmds', 'common'))

print(target_dir)
assert os.path.exists(target_dir)

#os.chdir(target_dir)
#os.system('python install.py')

sys.path.insert(0, target_dir)
from update import main
main()
