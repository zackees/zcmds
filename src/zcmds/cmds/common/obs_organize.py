import os
import shutil
from datetime import datetime
from os import path
from typing import List, Tuple

HOME_DIR = os.path.expanduser("~")
PATH_DEFAULT_OBS = os.path.join(HOME_DIR, "Videos", "obs")
DRY_RUN = False


def _is_video_file(file_path: str) -> bool:
    """Returns True if the given file is a video file."""
    _, ext = os.path.splitext(file_path.lower())
    return ext in [".mp4", ".mkv"]


def makedirs(new_dir: str, exist_ok: bool = False) -> None:
    """Make the given directory."""
    print(f"make_dirs: {new_dir}")
    if not DRY_RUN:
        os.makedirs(new_dir, exist_ok=exist_ok)


def movefile(src: str, dst: str) -> None:
    """Move the given file."""
    print(f"movefile: {src} -> {dst}")
    if not DRY_RUN:
        shutil.move(src, dst)


def parse_filename(file_path: str) -> Tuple[datetime, str]:
    """Parse the filename to extract date and time, or use file creation time if parsing fails."""
    filename = path.basename(file_path)
    name, ext = path.splitext(filename)
    # Extract the first 19 characters which should be the date and time
    date_time_str = name[:19]
    try:
        # Try parsing with underscore format first
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        try:
            # If that fails, try the space format
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H-%M-%S")
        except ValueError:
            # If both fail, use the file's creation time
            creation_time = path.getctime(file_path)
            date_time = datetime.fromtimestamp(creation_time)
            print(f"Using file creation time for: {filename}")
    return date_time, ext


def organize(path: str = PATH_DEFAULT_OBS) -> None:
    """Organize the given path."""
    video_files: List[str] = [f for f in os.listdir(path) if _is_video_file(f)]

    for video_file in video_files:
        try:
            file_path = os.path.join(path, video_file)
            date_time, ext = parse_filename(file_path)

            new_dir = os.path.join(
                path,
                str(date_time.year),
                f"{date_time.month:02d}",
                f"{date_time.day:02d}",
            )
            new_filename = f"{date_time.strftime('%Y-%m-%d %H-%M-%S')}{ext}"
            new_path = os.path.join(new_dir, new_filename)

            makedirs(new_dir, exist_ok=True)
            movefile(file_path, new_path)
        except Exception as e:
            print(f"Error processing {video_file}: {str(e)}")


def main() -> None:
    """Main entry point."""
    reply = input(
        f"WARNING! This will organize all your videos in the obs path:\n  {PATH_DEFAULT_OBS}\ncontinue? [y/n]: "
    )
    if reply.lower() == "y":
        organize()
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    main()
