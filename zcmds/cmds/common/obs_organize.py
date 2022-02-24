import os
import shutil
import traceback

HOME_DIR = os.path.abspath(os.path.expanduser("~"))
PATH_DEFAULT_OBS = os.path.join(HOME_DIR, "videos", "obs")
DRY_RUN = False


def _is_video_file(file_path: str) -> bool:
    """Returns True if the given file is a video file."""
    _, ext = os.path.splitext(file_path.lower())
    return ext in [".mp4", ".mkv"]


def makedirs(new_dir: str, exist_ok: bool = False) -> None:
    """Make the given directory."""
    print(f"make_dirs: {new_dir}")
    if DRY_RUN:
        return
    os.makedirs(new_dir, exist_ok=exist_ok)


def movefile(src: str, dst: str) -> None:
    """Move the given file."""
    print(f"movefile: {src} -> {dst}")
    if DRY_RUN:
        return
    shutil.move(src, dst)


def organize(path: str = PATH_DEFAULT_OBS) -> None:
    """Organize the given path."""
    paths = [os.path.join(path, p) for p in os.listdir(path) if _is_video_file(p)]
    for p in paths:
        try:
            name_ext = os.path.basename(p)
            name = os.path.splitext(name_ext)[0]
            ext = os.path.splitext(name_ext)[1]
            date_time = name.replace(" ", "_").split("_")
            new_dir = os.path.join(path, date_time[0])
            new_path = os.path.join(new_dir, f"{date_time[1]}{ext}")
            makedirs(os.path.dirname(new_path), exist_ok=True)
            movefile(p, new_path)
        except Exception as e:
            traceback.print_exc()
            print(f"Could not process {p} because of {e}")


def main() -> None:
    """Main entry point."""
    reply = input(
        f"WARNING! This will organize all your videos in the obs path:\n  {PATH_DEFAULT_OBS}\ncontinue? [y/n]: "
    )
    if reply.lower() != "y":
        organize()


if __name__ == "__main__":
    main()
