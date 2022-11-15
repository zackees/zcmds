# pylint: skip-file

import argparse
import os
import platform
import subprocess
import sys

# import dataclass
from dataclasses import dataclass
from threading import Thread

from beepy import beep  # type: ignore
from PyQt6 import QtCore  # type: ignore
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow  # type: ignore


@dataclass
class VidInfo:
    vidbitrate: str
    height: int


def encode(videopath: str, vidinfos: list[VidInfo]) -> None:
    path, _ = os.path.splitext(videopath)
    os.makedirs(path, exist_ok=True)
    for vidinfo in vidinfos:
        height = vidinfo.height
        vidbitrate = vidinfo.vidbitrate
        bitrate_str = vidbitrate.replace(".", "_")
        out_path = os.path.join(path, f"{height}_{bitrate_str}.mp4")
        downmix_stmt = "-ac 1" if height <= 480 else ""
        # trunc(oh*...) fixes issue with libx264 encoder not liking an add number of width pixels.
        null_stm: str = "/dev/null" if platform.system() != "Windows" else "NUL"
        cmd_1stpass = (
            f'static_ffmpeg -y -hide_banner -v quiet -stats -i "{videopath}"'
            f' -vf scale="trunc(oh*a/2)*2:{height}" {downmix_stmt}'
            " -movflags +faststart -preset veryslow -c:v libx264"
            f" -an -pass 1 -f null {null_stm}"
            f' -b:v {vidbitrate} "{out_path}"'
        )

        cmd_2ndpass = (
            f'static_ffmpeg -y -hide_banner -v quiet -stats -i "{videopath}"'
            f' -vf scale="trunc(oh*a/2)*2:{height}" {downmix_stmt}'
            " -movflags +faststart -preset veryslow -c:v libx264"
            f' -pass 2 -b:v {vidbitrate} "{out_path}"'
        )
        print(f"\nRunning first pass:\n  {cmd_1stpass}\n")
        proc = subprocess.Popen(cmd_1stpass, shell=True)
        proc.wait()
        print(f"\nRunning second pass:\n  {cmd_2ndpass}\n")
        proc = subprocess.Popen(cmd_2ndpass, shell=True)
        proc.wait()
        print(
            f"\n########################\n# Generated file:\n#  {out_path}\n########################"
        )


class MainWidget(QMainWindow):
    def __init__(self, on_drop_callback):
        super().__init__()
        self.setWindowTitle("Vidwebmaster")
        self.resize(720, 480)
        self.setAcceptDrops(True)
        # Add a label to the window on top of everythign elese
        self.label = QLabel(self)
        # Adjust label so it is centered
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setText("    Drag and Drop Large Video File Here")
        self.label.adjustSize()
        self.on_drop_callback = on_drop_callback

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            self.on_drop_callback(f)


def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def run_gui(vidinfos: list[VidInfo]) -> None:
    app = QApplication(sys.argv)

    def callback(videofile):
        path, _ = os.path.splitext(videofile)
        os.makedirs(path, exist_ok=True)
        open_folder(path)

        # Open folder in the OS
        def _encode_then_beep():
            encode(videofile, vidinfos=vidinfos)
            # do a beep when done
            beep(sound="ping")

        Thread(target=_encode_then_beep, daemon=True).start()

    ui = MainWidget(callback)
    ui.show()
    sys.exit(app.exec())


def parse_vidinfos(vidinfos_str: str) -> list[VidInfo]:
    vidinfos = []
    for vidinfo_str in vidinfos_str.split(","):
        height, bitrate = vidinfo_str.split(":")
        vidinfos.append(VidInfo(vidbitrate=bitrate, height=int(height)))
    # sort so that smallest resolution is first
    vidinfos.sort(key=lambda x: x.height)
    return vidinfos


def main():
    # Expects a single argument: the path to the video file to shrink
    parser = argparse.ArgumentParser(description="Make Web masters at 480, 720 and 1080p")
    parser.add_argument("video_path", help="Path to the video file to shrink", nargs="?")
    # Adds optional height argument
    parser.add_argument(
        "--encodings",
        help="height of the output video, e.g 1080 = 1080p",
        default="1080:3.0M,720:1.6M,480:0.9M",
    )
    args = parser.parse_args()
    vidinfos = parse_vidinfos(args.encodings)
    # sort by smallest first
    if not args.video_path:
        run_gui(vidinfos)
        return
    videopath = args.video_path
    if not os.path.exists(videopath):
        print(f"{videopath} does not exist")
        sys.exit(1)
    encode(args.video_path, vidinfos)


if __name__ == "__main__":
    main()
