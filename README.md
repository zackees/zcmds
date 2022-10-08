# zcmds
Cross platform(ish) productivity commands written in python. Tools for doing video and searching through files.

More information will be added later.


[![Actions Status](https://github.com/zackees/zcmds/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_macos.yml)
[![Actions Status](https://github.com/zackees/zcmds/workflows/Win_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_win.yml)
[![Actions Status](https://github.com/zackees/zcmds/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_ubuntu.yml)


# Commands

  * audnorm
  * diskaudit
  * git-bash
  * obs_organize
  * pdf2png
  * search_and_replace
  * search_in_files
  * sharedir
  * stereo2mono
  * stripaudio
  * vid2gif
  * vid2jpg
  * vid2mp3
  * vid2mp4
  * vidclip
  * viddur
  * vidshrink
  * vidspeed
  * vidvol
  * ytclip


# Install (normal)
  * `python -pip install zcmds`


# Install (dev):

  * `git clone https://github.com/zackees/zcmds`
  * `cd zcmds`
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

# Release Notes
  * 1.1.16: vidwebmaster fixes heights argument for other code path
  * 1.1.16: vidwebmaster fixes heights argument
  * 1.1.15: vidwebmaster fixed
  * 1.1.14: QT5 -> QT6
  * 1.1.13: vidwebmaster fixes () bash-bug in linux
  * 1.1.12: vidwebmaster now has a gui if no file is supplied
  * 1.1.11: Adds vidlist
  * 1.1.10: Adds vidhero
  * 1.1.9: adds vidwebmaster
  * 1.1.8: adds vidmatrix to test out different settings.
  * 1.1.7: vidshrink and vidclip now both feature width argument
  * 1.1.6: Adds touch to win32
  * 1.1.5: Adds unzip to win32
  * 1.1.4: Fix home cmd.
  * 1.1.3: Fix up cmds so it returns int
  * 1.1.2: Fix git-bash on win32
  * 1.1.1: Release
