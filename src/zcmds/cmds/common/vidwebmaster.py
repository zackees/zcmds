# pylint: skip-file

import argparse
import os
import platform
import subprocess
import sys
from threading import Thread

from beepy import beep  # type: ignore
from PyQt6 import QtCore  # type: ignore
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow  # type: ignore


def encode(videopath: str, crf: int, heights: list[int]) -> None:
    path, _ = os.path.splitext(videopath)
    os.makedirs(path, exist_ok=True)
    for height in heights:
        out_path = os.path.join(path, f"{height}_{crf}.mp4")
        downmix_stmt = "-ac 1" if height <= 480 else ""
        # trunc(oh*...) fixes issue with libx264 encoder not liking an add number of width pixels.
        cmd = f'static_ffmpeg -hide_banner -i "{videopath}" -vf scale="trunc(oh*a/2)*2:{height}" {downmix_stmt} -movflags +faststart -preset veryslow -c:v libx264 -crf {crf} "{out_path}" -y'
        print(f"Running:\n  {cmd}")
        # os.system(cmd)
        # startupinfo = subprocess.STARTUPINFO()
        # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(cmd, shell=True)
        proc.wait()
        print("Generted file: " + out_path)


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


def run_gui(crf: int, heights: list[int]) -> None:
    app = QApplication(sys.argv)

    def callback(videofile):
        path, _ = os.path.splitext(videofile)
        os.makedirs(path, exist_ok=True)
        open_folder(path)

        # Open folder in the OS
        def _encode_then_beep():
            encode(videofile, crf, heights)
            # do a beep when done
            beep(sound="ping")
        Thread(target=_encode_then_beep, daemon=True).start()
    ui = MainWidget(callback)
    ui.show()
    sys.exit(app.exec())


def main():
    # Expects a single argument: the path to the video file to shrink
    parser = argparse.ArgumentParser(
        description="Make Web masters at 480, 720 and 1080p"
    )
    parser.add_argument("video_path", help="Path to the video file to shrink", nargs="?")
    # Adds optional crf argument
    parser.add_argument("--crf", help="CRF value to use", type=int, default=28)
    # Adds optional height argument
    parser.add_argument(
        "--heights",
        help="height of the output video, e.g 1080 = 1080p",
        default="1080,720,480",
    )
    args = parser.parse_args()
    heights = [int(h) for h in args.heights.split(",")]
    if not args.video_path:
        run_gui(args.crf, heights)
        return
    videopath = args.video_path
    if not os.path.exists(videopath):
        print(f"{videopath} does not exist")
        sys.exit(1)
    encode(args.video_path, args.crf, heights)


if __name__ == "__main__":
    main()
