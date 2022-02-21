import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

# The directory containing this file
HERE = os.path.dirname(__file__)

NAME = "productivity_cmds"
DESCRIPTION = "Command to download a video and cut out a clip."
URL = f"https://github.com/zackees/{NAME}"
EMAIL = "dont@email.me"
AUTHOR = "Zach Vorhies"
REQUIRES_PYTHON = ">=3.6.0"
VERSION_FILE = os.path.join(HERE, NAME, "version.py")
README_FILE = os.path.join(HERE, "README.md")
REQUIREMENTS_FILE = os.path.join(HERE, "requirements.txt")

# The text of the README file
with open(README_FILE, encoding="utf-8", mode="rt") as fd:
    LONG_DESCRIPTION = fd.read()

with open(REQUIREMENTS_FILE, encoding="utf-8", mode="rt") as fd:
    REQUIREMENTS = [line.strip() for line in fd.readlines() if line.strip()]

with open(VERSION_FILE, encoding="utf-8", mode="rt") as fd:
    for line in fd.readlines():
        if "VERSION" in line:
            if "#" in line:  # Remove comments
                line = line.split("#")[0]
            VERSION = line.split("=")[1].strip(" \n\"")
            print(VERSION)
            break

class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        pass

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(HERE, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system('"{0}" setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(VERSION))
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    python_requires=REQUIRES_PYTHON,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    author="Zach Vorhies",
    author_email="dont@email.me",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: Console",
    ],
    install_requires=REQUIREMENTS,

    entry_points={
        "console_scripts": [
            "zcmds_install = productivity_cmds.cmds.common.update:main",
            "zcmds = productivity_cmds.cmds.common.zcmds:main",
        ],
    },
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    package_data={},
    include_package_data=True,
    extras_require={
        "test": ["pytest"],
    },
    cmdclass={
        "upload": UploadCommand,
    },
)
