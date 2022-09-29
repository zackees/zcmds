import json
import os
import sys
from pprint import pprint
from shutil import rmtree

from setuptools import Command, find_packages, setup

# The directory containing this file
PROJECT_ROOT = os.path.dirname(__file__)

NAME = "zcmds"
DESCRIPTION = "Cross platform(ish) productivity commands written in python."
URL = f"https://github.com/zackees/{NAME}"
EMAIL = "dont@email.me"
AUTHOR = "Zach Vorhies"
REQUIRES_PYTHON = ">=3.6.0"
VERSION_FILE = os.path.join(PROJECT_ROOT, NAME, "version.py")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")
REQUIREMENTS_FILE = os.path.join(PROJECT_ROOT, "requirements.txt")

BINDINGS_JS_FILE = os.path.join(PROJECT_ROOT, NAME, "cmds", "bindings.json.py")
with open(BINDINGS_JS_FILE, encoding="utf-8", mode="rt") as fd:
    BINDINGS_JSON = json.load(fd)

bindings = BINDINGS_JSON["common"]
if sys.platform == "win32":
    bindings.extend(BINDINGS_JSON["win32"])

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
            VERSION = line.split("=")[1].strip(' \n"')
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
            rmtree(os.path.join(PROJECT_ROOT, "dist"))
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


package_data = []

# walk through zcmds directory and add all files to package_data
for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "zcmds", "cmds")):
    for file in files:
        package_data.append(os.path.join(root, file))

for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "zcmds", "install")):
    for file in files:
        package_data.append(os.path.join(root, file))

# Make all package_data files relative to PROJECT_ROOT
package_data = [os.path.relpath(path, PROJECT_ROOT) for path in package_data]

pprint(package_data)

# import module and get the bindings

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
    entry_points={"console_scripts": bindings},
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    package_data={
        "zcmds": package_data,
    },
    include_package_data=True,
    extras_require={
        "test": ["pytest"],
    },
    cmdclass={
        "upload": UploadCommand,
    },
)
