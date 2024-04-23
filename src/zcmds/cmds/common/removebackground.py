import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PORT = 5283


def install_rembg_if_missing() -> None:
    bin_path = os.path.expanduser("~/.local/bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + bin_path
    if shutil.which("rembg") is not None:
        return
    print("Installing rembg...")
    os.system("pipx install rembg[cli]")
    assert shutil.which("rembg") is not None, "rembg not found after install"


def open_browser_with_delay(url: str, delay: float) -> None:
    def delayed_open():
        time.sleep(delay)
        webbrowser.open(url)

    threading.Thread(target=delayed_open).start()


@dataclass
class VidInfo:
    width: int
    height: int
    fps: float


def get_video_info(video_path: Path) -> VidInfo:
    # use static_ffmpeg to get the video dimensions using the ffprobe and the
    # json output feature
    command = f'vidinfo "{video_path}"'
    stdout = subprocess.check_output(command, shell=True).decode("utf-8")
    lines = stdout.split("\n")
    height: Optional[int] = None
    width: Optional[int] = None
    fps: Optional[float] = None
    for line in lines:
        if "Height: " in line:
            height = int(line.split("Height: ")[1])
        if "Width: " in line:
            width = int(line.split("Width: ")[1])
        if "Framerate: " in line:
            fps_str = line.split("Framerate: ")[1]
            # split out the " fps" part
            fps = float(fps_str.split(" ")[0])
    assert height is not None, "Height not found in video info"
    assert width is not None, "Width not found in video info"
    assert fps is not None, "Framerate not found in video info"
    # return width, height, fps
    return VidInfo(width, height, fps)


def video_remove_background(video_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    vidinfo: VidInfo = get_video_info(video_path)
    # print(width_x_height)
    print(f"Video dimensions: {vidinfo.width}x{vidinfo.height}")
    cmd = f"static_ffmpeg -i {video_path} {output_dir}/%05d.png"
    rtn = os.system(cmd)
    if rtn != 0:
        raise OSError("Error converting video to images")  # pragma: no cover
    print(f"Images saved to {output_dir}")
    # now run rembg on the images
    # ffmpeg -i input.mp4 -ss 10 -an -f rawvideo -pix_fmt rgb24 pipe:1 | rembg b 1280 720 -o folder/output-%03u.png
    # cmd = f'rembg b {width} {height} -o "{output_dir}/%05d.png"'
    final_output_dir = output_dir / "video"
    final_output_dir.mkdir(parents=True, exist_ok=True)
    cmd = f'rembg p "{output_dir}" "{final_output_dir}"'
    print(f"Running: {cmd}")
    os.system(cmd)
    print(f"Images with background removed saved to {final_output_dir}")
    # now convert the images back to video
    fps: float = vidinfo.fps
    out_vid_path = Path(str(video_path.with_suffix("")) + "-removed-background.mp4")
    cmd = f'static_ffmpeg -framerate {fps} -i "{final_output_dir}/%05d.png" -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p "{out_vid_path}"'
    print(f"Running: {cmd}")
    os.system(cmd)


def is_video_file(file_path: Path) -> bool:
    return file_path.suffix in {".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm", ".wmv"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove background from images")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=PORT,
        help=f"Port to run the server on (default: {PORT})",
    )

    parser.add_argument(
        "file",
        type=Path,
        nargs="?",
    )

    return parser.parse_args()


def cli() -> int:
    install_rembg_if_missing()
    args = parse_args()
    if args.file is not None:
        if is_video_file(args.file):
            video_remove_background(args.file, args.file.with_suffix(""))
            return 0
        return os.system(f'rembg i "{args.file}"')
    open_browser_with_delay(f"http://localhost:{PORT}", 4)
    os.system(f"rembg s --port {PORT}")
    return 0


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.argv.append("--file")
    sys.argv.append("info-second.mp4")
    sys.exit(main())
