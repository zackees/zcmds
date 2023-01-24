# zcmds
Cross platform(ish) productivity commands written in python. Tools for doing video manipulation, searching through files and other things. On Windows ls, rm and other common unix file commands are installed.

[![Actions Status](https://github.com/zackees/zcmds/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_macos.yml)
[![Actions Status](https://github.com/zackees/zcmds/workflows/Win_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_win.yml)
[![Actions Status](https://github.com/zackees/zcmds/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_ubuntu.yml)

[![Linting](https://github.com/zackees/zcmds/actions/workflows/lint.yml/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/lint.yml)

# Install

```bash
> pip install zmcds
> zcmds
> diskaudit
```

# Commands

  * askai
  * audnorm
  * comports
  * diskaudit
  * git-bash
  * findfile
  * obs_organize
  * printenv
  * pdf2png
  * search_and_replace
  * search_in_files
  * sharedir
  * stereo2mono
  * vidmute
  * vidinfo
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


# Install (dev):

  * `git clone https://github.com/zackees/zcmds`
  * `cd zcmds`
  * `python -pip install -e .`
  * Test by typing in `zcmds`


# Additional install

  For the pdf2image use:
  * win32: `choco install poppler`
  * ... ?

# Note:

Running tox will install hooks into the .tox directory. Keep this in my if you are developing.
TODO: Add a cleanup function to undo this.

# Release Notes
  * 1.3.11: Fix badges.
  * 1.3.10: Suppress spurious warnings with chardet in openai
  * 1.3.9: Changes sound driver, should eliminate the runtime dependency on win32.
  * 1.3.8: Adds askai tool
  * 1.3.7: findfile -> findfiles
  * 1.3.6: zcmds[win32] is now at 1.0.2 (includes `unzip`)
  * 1.3.5: zcmds[win32] is now at 1.0.1 (includes `nano` and `pico`)
  * 1.3.4: Adds `printenv` utility
  * 1.3.3: Adds `findfile` utility.
  * 1.3.2: Adds `comports` to display all comports that are active on the computer.
  * 1.3.1: Nit improvement in search_and_replace to improve ui
  * 1.3.0: vidwebmaster now does variable rate encoding. --crf and --heights has been replaced by --encodings
  * 1.2.1: Adds improvements to vidhero for audio fade and makes vidclip improves usability
  * 1.2.0: stripaudio -> vidmute
  * 1.1.30: Improves vidinfo with less spam on the console and allows passing height list
  * 1.1.29: More improvements to vidinfo
  * 1.1.28: vidinfo now has more encodingg information
  * 1.1.27: Fix issues with spaces in vidinfo
  * 1.1.26: Adds vidinfo
  * 1.1.26: Vidclip now supports start_time end_time being omitted.
  * 1.1.25: Even better performance of diskaudit. 50% reduction in execution time.
  * 1.1.24: Fixes diskaudit from double counting
  * 1.1.23: Fixes test_net_connection
  * 1.1.22: vid2mp4 - if file exists, try another name.
  * 1.1.21: Adds --fps option to vidshrink utility
  * 1.1.19: Using pyprojec.toml build system now.
  * 1.1.17: vidwebmaster fixes heights argument for other code path
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


# TODO:

  * Add silence remover:
    * https://github.com/bambax/Remsi
  * Add lossless cut to vidclip
    * https://github.com/mifi/lossless-cut
