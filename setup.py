import os
import re

import setuptools

URL = "https://github.com/zackees/zcmds"

HERE = os.path.dirname(os.path.abspath(__file__))

def get_version() -> str:
    """Get the version from the version.py file."""
    version_py = os.path.join(HERE, "src", "zcmds", "version.py")
    # version looks like VERSION = "1.4.31"
    with open(version_py, encoding="utf-8", mode="r") as version_file:
        version = version_file.read()
    version = version.split("VERSION = ")[1].split('"')[1]
    # remove comment block that's after
    version = version.split("#")[0]
    version = version.strip()
    return version


def get_readme() -> str:
    """Get the contents of the README file."""
    readme = os.path.join(HERE, "README.md")
    with open(readme, encoding="utf-8", mode="r") as readme_file:
        readme_lines = readme_file.readlines()
    return "".join(readme_lines)


def get_console_scripts() -> list[str]:
    cmds_txt = os.path.join(HERE, "src", "zcmds", "cmds.txt")
    with open(cmds_txt, encoding="utf-8", mode="r") as cmds_file:
        cmds = cmds_file.readlines()
    cmds = [cmd.replace('"', "").strip() for cmd in cmds]
    return cmds


if __name__ == "__main__":
    setuptools.setup(
        maintainer="Zachary Vorhies",
        long_description=get_readme(),
        long_description_content_type="text/plain",
        url=URL,
        package_data={"": ["assets/bell.mp3"]},
        include_package_data=True,
        version=get_version(),
        entry_points={
            "console_scripts": [get_console_scripts()],
        },
    )
