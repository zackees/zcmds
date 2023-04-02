import os
import re

import setuptools

URL = "https://github.com/zackees/zcmds"

HERE = os.path.dirname(os.path.abspath(__file__))


def get_readme() -> str:
    """Get the contents of the README file."""
    readme = os.path.join(HERE, "README.md")
    with open(readme, encoding="utf-8", mode="r") as readme_file:
        readme_lines = readme_file.readlines()
    for i, line in enumerate(readme_lines):
        if "../../" in line:
            # Transform the relative links to absolute links
            output_string = re.sub(r"(\.\./\.\.)", f"{URL}", line, count=1)
            output_string = re.sub(r"(\.\./\.\.)", f"{URL}", output_string)
            readme_lines[i] = output_string
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
        long_description_content_type="text/markdown",
        url=URL,
        package_data={"": ["assets/bell.mp3"]},
        include_package_data=True,
        entry_points={
            "console_scripts": [get_console_scripts()],
        },
    )
