# zcmds
Cross platform(ish) productivity commands written in python. Tools for doing media manipulation through ffmpeg and AI. On Windows ls, rm and other common unix file commands are installed. Whenever there is something that doesn't work on Windows but does on Mac/Linux, I will apply a tool to make it work here. This toolset is ever-evolving and it's going to get insane in 2024 with all the AI that I'm now integrating.

[![MacOS_Tests](https://github.com/zackees/zcmds/actions/workflows/push_macos.yml/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_macos.yml)
[![Win_Tests](https://github.com/zackees/zcmds/actions/workflows/push_win.yml/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_win.yml)
[![Ubuntu_Tests](https://github.com/zackees/zcmds/actions/workflows/push_ubuntu.yml/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/push_ubuntu.yml)

[![Linting](https://github.com/zackees/zcmds/actions/workflows/lint.yml/badge.svg)](https://github.com/zackees/zcmds/actions/workflows/lint.yml)

# Install

```bash
> pip install zcmds
> zcmds  # shows all commands
> diskaudit  # audits the disk usage from the current directory.
```

# Commands

  **Remember that typing in `zcmds` at the terminal will show you all the commands**

  * archive
    * Zips up the specified directory or file.
  * askai
    * Asks a question to OpenAI from the terminal command. Requires an openai token which will be requested and saved on first use.
    * Prefix your query with `!` to run command directly.
  * aicode
    * A front end for `Aider`, an AI pair programming tool. This is the future the sci fi writers promised you.
  * audnorm
    * Normalizes audio in a media file to a standard volume.
  * codeup
    * If your current git repo has `./lint`, `./test`, then this tool will run them in this order. If they both pass then
      `git add .` followed by `git commit -m ` or `aicommits` will be invoked.
  * comports
    * Shows all the ports that are in use at the current computer (useful for Arduino debugging).
  * diskaudit
    * walks the directory from the current directory and catalogs which of the child folders take up the most space.
  * git-bash (win32)
    * launches git-bash terminal (windows only).
  * gitconfig
    * Configures git so that it's in "easy-to-use-mode".
  * gitsummary
    * Generates a summary of the git repository commits, useful for invoicing
  * findfiles
    * finds a file with the given glob.
  * img2webp
    * Conversion tool for converting images into webp format.
  * img2vid
    * Converts a series of images to a video.
  * obs_organize
    * organizes the files in your default obs directory.
  * merge-to
    * Merges a clean git repo (no untracked files) to the target branch, pushes that target branch, then switches back to the original branch.
  * new
    * Opens a new terminal command window from the current terminal command window.
  * printenv
    * prints the current environment variables, including path. Everything is sorted
  * pdf2png
    * Converts a pdf to a series of images
  * pdf2txt
    * Converts a pdf to a text file.
  * push
    * A safer way to `git push`, checks if the rebase is dirty.
  * removbackground
    * Launches an AI tool in the browser to remove the background from an Image. Can also generate video with background removed. Front end for `rembg` backend.
  * search_and_replace
    * Search all the files from the current directory and applies exact text search and replace.
  * search_in_files
    * Search all files from current working directory for exact string matches matches.
  * sharedir
    * takes the current folder and shares it via a reverse proxy using ngrok.
  * stereo2mono
    * Reduces a stereo audio / video to a single mono track.
  * sudo (win32 only)
    * Runs a command as in sudo, using the gsudo tool.
  * vidcat
    * Concatenates two videos together, upscaling a lower resolution video.
  * vidmute
    * Strips out the audio in a video file and saves it as a new file.
  * vidinfo
    * Uses ffprobe to find the information from a video file.
  * vid2gif
    * A video is converted into an animated gif.
  * vid2jpg
    * A video is converted to a series of jpegs.
  * vid2mp3
    * A video is converted to an mp3.
  * vid2mp4
    * A video is converted to mp4. Useful for obs which saves everything as mkv. Extremely fast with mkv -> mp4 converstion.
  * vidclip
    * Clips a video using timestamps.
  * viddur
    * Get's the during, use vidinfo instead.
  * vidshrink
    * Shrinks a video. Useful for social media posts.
  * vidspeed
    * Changes the speed of a video.
  * vidvol
    * Changes the volume of a video.
  * ytclip
    * Download and clip a video from a url from youtube, rumble, bitchute, twitter... The timestamps are prompted by this program.
  * trash
    * Sends the folder or files to the trash. This sometimes works better than deleting files on Windows.
  * whichall
    * Finds all the executables in the path.
  * unzip
    * unzip the provided file
  * fixinternet
    * Attempts to fix the internet connection by flushing the dns and resetting the network adapter.
  * fixvmmem (win32 only)
    * Fixes the vmmem consuming 100% cpu on windows 10 after hibernate.
  * transcribe-anything
    * Transcribe media content using state of the art insanely-fast-whisper
  * tx
    * Easily send files over the internet. `tx README.md`
      * Front end to `womrhole send file`, but gives you the code upfront so the client can auto connect.

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
  * 1.4.83: `removebackground` now uses `-b` for bitrate for mp4 like it does webm. Bitrates can now be specified in other units like 500k.code
  * 1.4.82: `removebackground` now generates an mp4 encoded in HEVC for yuva420p support as well as webm with vp9 yuva420p.
  * 1.4.81: `aicode` now defaults to `--claude3` if anthropic key is set. `removebackground` now supports parallel processing.
  * 1.4.80: `aicode` now supports `--claude3`, use `--set-anthropic-key` to set the key.
  * 1.4.79: `removebackground` now allows `--fps`
  * 1.4.78: `removebackground` now allows `--height`
  * 1.4.77: `removebackground` now allows video/image as input.
  * 1.4.76: `askai` now had `--input-file`, for better tooling.
  * 1.4.75: Fix https://github.com/zackees/zcmds/issues/13 in `img2webp`
  * 1.4.74: Fix `https://github.com/zackees/zcmds/issues/901`
  * 1.4.73: `aicode` now accepts Windows paths and converts them to posix paths prior to sending them to Aider.
  * 1.4.72: `aicode` is now 2x faster to load because checking update version is now a delayed background task.
  * 1.4.71: `codeup` now finds `.git` directory a few parents up, also allows `--no-test`
  * 1.4.70: `askai` now has `--assistant-prompt-file`
  * 1.4.69: `codeup` now implies `--push`. If you don't want to push then use `--no-push``
  * 1.4.68: `codeup` now has `--push` to allow pushes to the repo if everything passes.
  * 1.4.67: Adds new tool `codeup` which will run ./lint (if it exists) then ./test (if it exists) then aicommits (if it exists)
  * 1.4.66: `askai` now allows optional `--assistant-prompt` to tell the AI what it is. This is super useful for data scientists, you can use this in your Jupyter Notebooks quite easily!
  * 1.4.65: Adds `gitconfig`
  * 1.4.64: Adds `new` to open a new terminal command window from the current terminal command window.
  * 1.4.63: Adds `gitconfigure` to give sane defaults to your git.
  * 1.4.62: `askai` can now run commands by prefixing with `!`
  * 1.4.61: Fix bug in `tx`
  * 1.4.60: New tool `tx`, a wrapper around `wormhole send` but easier to use.
  * 1.4.59: New tool `push`, a safe way to `git push`
  * 1.4.58: Fixes `askai` with positional args (asking a question and then immediatly exiting.)
  * 1.4.57: Bring in new `zcmds_win32` include `sshpass`
  * 1.4.56: Fixes `aicode` on first run crash.
  * 1.4.54: Bring in new `zcmds_win32` fixes and improvements.
  * 1.4.53: Fixes `transcribe-anything` with python 3.11 for `--device insane`
  * 1.4.52: Update `transcribe-anything` for bug fix 2.7.23
  * 1.4.51: Updates `transcribe-anything` to 2.7.22
  * 1.4.50: Uses git-bash version of ssh for windows.
  * 1.4.49: Adds `trash` which sends files to the trash.
  * 1.4.48: Adds `removebackground` which uses AI to remove a background image. Uses `rembg` backend
  * 1.4.47: Adds `transcribe-anything` to the command stack.
  * 1.4.46: Fix `merge-to` with missing push step from target step.
  * 1.4.45: Adds new tool `merge-to`, which streamlines merge a current branch into the other and then pushing.
  * 1.4.44: Fixes vidwebmaster (Qt6 pinned version just stopped working!!)
  * 1.4.43: Adds `aicode` which is the same as `askai --code`
  * 1.4.42: Adds `imgshrink`
  * 1.4.41: `aider` now installed with `pipx` to avoid package conflicts because of it's pinned deps.
  * 1.4.40: Fix `askai` in python 3.11 with linux.
  * 1.4.39: `aider` is now part of this command set. An awesome ai pair programmer. Enable it with `askai --code`
  * 1.4.37: `askai` now streams output to the console.
  * 1.4.36: `losslesscut` (on windows) can now be executed on other drivers and doesn't block the current terminal.
  * 1.4.35: `askai` now assumed `--fast`. You can use gpt4 vs `--slow`
  * 1.4.34: Fixes geninvoice
  * 1.4.32: OpenAI now requires version 1.3.8 or higher (fixes breaking changes from OpenAI)
  * 1.4.31: Improve `audnorm` so that it uses sox instead of `ffmpeg-normalize`. Fix bug where not all commands were installed. Fixes openai api changes.
  * 1.4.30: Fix error in diskaudit when no files found in protected dir.
  * 1.4.29: Fix img2webp.
  * 1.4.28: Bug fix
  * 1.4.27: askai now has `--fast`
  * 1.4.26: vid2jpg now has `--no-open-folder`
  * 1.4.24: Adds `archive`
  * 1.4.23: Bump zcmds-win32
  * 1.4.21: `askai` handles pasting text that has double lines in it.
  * 1.4.20: `askai` is now at gpt-4
  * 1.4.19: Adds `losslesscut` for win32.
  * 1.4.18: Fix win32 `zcmds_win32`
  * 1.4.17: `vid2mp4` now adds `--nvenc` and `--height` `--crf`
  * 1.4.16: Fixes `img2webp`.
  * 1.4.15: Adds `img2webp` utility.
  * 1.4.13: Add `--no-fast-start` to vidwebmaster.
  * 1.4.12: Fixes a bug in find files when an exception is thrown during file inspection.
  * 1.4.11: `findfiles` now has --start --end --larger-than --smaller-then
  * 1.4.10: `zcmds` now uses `get_cmds.py` to get all of the commands from the exe list.
  * 1.4.8: `audnorm` now encodes in mp3 format (improves compatibility). vid2mp3 now allows `--normalize`
  * 1.4.7: Fixes broken build.
  * 1.4.6: Adds `say` command to speak out the text you give the program
  * 1.4.5: Adds saved settings for gitsummary
  * 1.4.4: Adds `pdf2txt` command
  * 1.4.3: Adds `gitsummary` command
  * 1.4.2: Bump up zcmds_win32 to 1.0.17
  * 1.4.1: Adds 'whichall' command
  * 1.4.0: Askai now supports question-answer-question-... interactive mode
  * 1.3.17: Adds syntax highlighting to open askai tool
  * 1.3.16: Improves openai by using gpt 3.5
  * 1.3.15: Improve vidinfo for more data and be a lot faster with single pass probing.
  * 1.3.14: Improve vidinfo to handle non existant streams and bad files.
  * 1.3.13: Added `img2vid` command.
  * 1.3.12: Added `fixinternet` command.
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
  * 1.1.28: vidinfo now has more encoding information
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
