# zcmds
Cross platform(ish) productivity commands written in python. Tools for doing video and searching through files.

More information will be added later.


[![Actions Status](https://github.com/zackees/zcmds/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_macos.yml)
[![Actions Status](https://github.com/zackees/zcmds/workflows/Win_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_win.yml)
[![Actions Status](https://github.com/zackees/zcmds/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_ubuntu.yml)


# Install (normal)
  * `python -pip install zcmds`


# Install (dev):

  * `python -pip install -e .`
  * Test by typing in `zcmds`
  * `zcmds_install`

# Additional install

  For the pdf2image use:
  * win32: `choco install poppler`
  * ... ?

# Note:

Running tox will install hooks into the .tox directory. Keep this in my if you are developing.
TODO: Add a cleanup function to undo this.