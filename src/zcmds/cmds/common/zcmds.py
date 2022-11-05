"""
    Normalizes the audio of a video file.
"""
import sys

COMMON = [
    "audnorm",
    "diskaudit",
    "obs_organize",
    "pdf2png",
    "search_and_replace",
    "search_in_files",
    "sharedir",
    "stereo2mono",
    "stripaudio",
    "vid2gif",
    "vid2jpg",
    "vid2mp3",
    "vid2mp4",
    "vid2webm",
    "vidclip",
    "viddur",
    "vidspeed",
    "vidvol",
    "vidshrink",
    "vidmatrix",
    "vidwebmaster",
    "vidhero",
    "vidlist",
    "test_net_connection",
    "ytclip",
]

WIN32 = [
    "cat",
    "cp",
    "du",
    "grep",
    "home",
    "ls",
    "mv",
    "open",
    "rm",
    "which",
    "git-bash",
    "touch",
]


def main():
    cmds = COMMON
    if sys.platform == "win32":
        cmds.extend(WIN32)
    cmds = sorted(cmds)
    print("zcmds:")
    for cmd in cmds:
        print(f"  {cmd}")


if __name__ == "__main__":
    main()
