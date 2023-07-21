import os

HERE = os.path.dirname(os.path.abspath(__file__))

PYPROJET_TOML = os.path.join(HERE, "pyproject.toml")
VERSION_PY = os.path.join(HERE, "src", "zcmds", "version.py")


def read_utf8(filename: str) -> str:
    """Read a file as utf-8"""
    with open(filename, encoding="utf-8", mode="r") as f:
        return f.read()


def write_utf8(filename: str, data: str) -> None:
    """Write a file as utf-8"""
    with open(filename, encoding="utf-8", mode="w") as f:
        f.write(data)


PYPROJ_TXT = read_utf8(PYPROJET_TOML)
VERSION_TXT = read_utf8(VERSION_PY)

# get version from pyproject.toml
version = PYPROJ_TXT.split("version = ")[1].split('"')[1]
version2 = VERSION_TXT.split("VERSION = ")[1].split('"')[1]

assert version == version2

# parse version like "1.4.24"
major, minor, patch = version.split(".")
patch = str(int(patch) + 1)
new_version = ".".join([major, minor, patch])

# write version back to files
lines = read_utf8(PYPROJET_TOML).splitlines()
for i, line in enumerate(lines):
    if "version = " in line:
        lines[i] = 'version = "{}"'.format(new_version)
        break
write_utf8(PYPROJET_TOML, "\n".join(lines) + "\n")

lines = read_utf8(VERSION_PY).splitlines()
for i, line in enumerate(lines):
    if line.startswith("VERSION = "):
        lines[i] = 'VERSION = "{}"  # pylint: disable=R0801'.format(new_version)
        break
write_utf8(VERSION_PY, "\n".join(lines) + "\n")
