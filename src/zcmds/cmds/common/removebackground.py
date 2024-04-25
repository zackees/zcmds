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

MODEL = "u2net"

"""
u2net: A pre-trained model for general use cases.
u2netp: A lightweight version of u2net model.
u2net_human_seg: A pre-trained model for human segmentation.
u2net_cloth_seg: A pre-trained model for Cloths Parsing from human portrait. Here clothes are parsed into 3 category: Upper body, Lower body and Full body.
silueta: Same as u2net but the size is reduced to 43Mb.
isnet-general-use: A new pre-trained model for general use cases.
isnet-anime: A high-accuracy segmentation for anime character.
sam (download encoder, download decoder, source): A pre-trained model for any use cases.
"""

MODELS = {
    "u2net": "A pre-trained model for general use cases.",
    "u2netp": "A lightweight version of u2net model.",
    "u2net_human_seg": "A pre-trained model for human segmentation.",
    "u2net_cloth_seg": "A pre-trained model for Cloths Parsing from human portrait. Here clothes are parsed into 3 category: Upper body, Lower body and Full body.",
    "silueta": "Same as u2net but the size is reduced to 43Mb.",
    "isnet-general-use": "A new pre-trained model for general use cases.",
    "isnet-anime": "A high-accuracy segmentation for anime character.",
    "sam": "A pre-trained model for any use cases.",
}

MODEL_CHOICES = list(MODELS.keys())


@dataclass
class VidInfo:
    width: int
    height: int
    fps: float


def install_rembg_if_missing() -> None:
    bin_path = os.path.expanduser("~/.local/bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + bin_path
    if shutil.which("rembg") is not None:
        return
    print("Installing rembg...")
    os.system("pipx install rembg[cli,gpu]")
    assert shutil.which("rembg") is not None, "rembg not found after install"


def open_browser_with_delay(url: str, delay: float) -> None:
    def delayed_open():
        time.sleep(delay)
        webbrowser.open(url)

    threading.Thread(target=delayed_open).start()


def get_video_info(video_path: Path) -> VidInfo:
    # use static_ffmpeg to get the video dimensions using the ffprobe and the
    # json output feature
    assert shutil.which("vidinfo") is not None, "vidinfo not found"
    assert video_path.exists(), f"Video file not found: {video_path}"
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


def video_remove_background(
    video_path: Path,
    output_dir: Path,
    bitrate_megs: float,
    output_height: Optional[int] = None,
    model: str = MODEL,
    keep_files: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    vidinfo: VidInfo = get_video_info(video_path)
    print(f"Video dimensions: {vidinfo.width}x{vidinfo.height}")
    cmd = f"static_ffmpeg -y -i {video_path} {output_dir}/%07d.png"
    rtn = os.system(cmd)
    if rtn != 0:
        raise OSError("Error converting video to images")
    print(f"Images saved to {output_dir}")

    final_output_dir = output_dir / "video"
    final_output_dir.mkdir(parents=True, exist_ok=True)
    cmd = f'rembg p -a -ae 15 --post-process-mask -m {model} "{output_dir}" "{final_output_dir}"'
    print(f"Running: {cmd}")
    os.system(cmd)
    print(f"Images with background removed saved to {final_output_dir}")

    fps: float = vidinfo.fps
    out_vid_path = Path(str(video_path.with_suffix("")) + "-removed-background.webm")
    filter_stmt = ""
    if output_height is not None:
        filter_stmt = f'-vf "scale=-1:{output_height}"'
    cmd = f'static_ffmpeg -y -framerate {fps} -i "{final_output_dir}/%07d.png" {filter_stmt} -c:v libvpx-vp9 -b:v {bitrate_megs}M -an "{out_vid_path}"'
    print(f"Running: {cmd}")
    rtn = os.system(cmd)
    if rtn != 0:
        raise OSError("Error converting images to video")

    # Command to merge the audio from the original video with the new video
    final_output_path = Path(str(video_path.with_suffix("")) + "-nobackground.webm")
    cmd = f'static_ffmpeg -y -i "{out_vid_path}" -i "{video_path}" -c:v copy -c:a libvorbis -map 0:v:0 -map 1:a:0 "{final_output_path}"'
    print(f"Running: {cmd}")
    rtn = os.system(cmd)
    if rtn != 0:
        raise OSError("Error merging video and audio")

    # Delete intermediate files if --keep-files is not set
    if not keep_files:
        shutil.rmtree(output_dir, ignore_errors=True)
        os.remove(out_vid_path)


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

    parser.add_argument(
        "-b",
        "--bitrate",
        type=float,
        default=10.0,
        help="Bitrate for the output video (default: 10.0)",
    )
    parser.add_argument(
        "--height",
        type=int,
        help="Height of the output video (default: None)",
    )
    parser.add_argument(
        "--keep-files",
        action="store_true",
        help="Keep intermediate files (default: False)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=MODEL,
        choices=MODEL_CHOICES,
        help=f"Model to use (default: {MODEL}, choices: {MODEL_CHOICES})",
    )

    return parser.parse_args()


def cli() -> int:
    install_rembg_if_missing()
    args = parse_args()
    if args.file is not None:
        if is_video_file(args.file):
            video_remove_background(
                video_path=args.file,
                output_dir=args.file.with_suffix(""),
                bitrate_megs=args.bitrate,
                output_height=args.height,
                keep_files=args.keep_files,
                model=args.model,
            )
            return 0
        return os.system(
            f'rembg -a -ae 15 --post-process-mask -m {args.model} i "{args.file}"'
        )
    open_browser_with_delay(f"http://localhost:{PORT}", 4)
    os.system(f"rembg s --port {PORT}")
    return 0


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.argv.append("second-part.mp4")
    sys.argv.append("--height")
    sys.argv.append("480")
    sys.exit(main())
