"""
    Normalizes the audio of a video file.
"""

import argparse
import os
import subprocess

from static_ffmpeg import add_paths  # type: ignore
from static_sox import add_paths as add_paths_sox  # type: ignore


def ffprobe_duration(filename: str) -> float:
    """
    Uses ffprobe to get the duration of a video file.
    """
    cmd = f"static_ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}"
    result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    result = result.replace("\n", "").replace(" ", "")
    return float(result)


def _is_media_file(filename: str) -> bool:
    print(f"Is media file: {filename}")
    assert os.path.isfile(filename), f"{filename} is not a file"
    body, ext = os.path.splitext(filename)
    return ext in [".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav", ".m4a"]


def _convert_to_wav(path: str, out: str) -> None:
    """
    Converts a media file to a wav file.
    """
    assert _is_media_file(path), f"{path} is not a media file"
    if len(os.path.dirname(out)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    add_paths(weak=True)
    cmd = f'static_ffmpeg -y -i "{path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{out}"'
    print(f"Executing:\n  {cmd}")
    os.system(cmd)


def _convert_to_mp3(path: str, out: str) -> None:
    """
    Converts a media file to an AAC file with 192k bitrate.
    """
    assert _is_media_file(path), f"{path} is not a media file"
    if len(os.path.dirname(out)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    # Updated FFmpeg command for AAC conversion
    cmd = f'static_ffmpeg -y -i "{path}" -vn -acodec aac -b:a 192k "{out}"'
    print(f"Executing:\n  {cmd}")
    os.system(cmd)


def _replace_audio(in_vid_mp4: str, in_mp3: str, out_mp3) -> None:
    """
    Replaces the audio of a video file with an mp3 file.
    """
    assert _is_media_file(in_vid_mp4), f"{in_vid_mp4} is not a media file"
    assert _is_media_file(in_mp3), f"{in_mp3} is not a media file"
    if len(os.path.dirname(out_mp3)):
        os.makedirs(os.path.dirname(out_mp3), exist_ok=True)
    video_stmt = "-map 0:v"
    if (
        in_vid_mp4.endswith(".mp3")
        or in_vid_mp4.endswith(".wav")
        or in_vid_mp4.endswith(".m4a")
    ):
        video_stmt = ""
    cmd = f'static_ffmpeg -y -i "{in_vid_mp4}" -i "{in_mp3}" {video_stmt} -map 1:a -c copy -shortest "{out_mp3}"'
    print(f"Executing:\n  {cmd}")
    rtn = os.system(cmd)
    if rtn == 0:
        return  # success
    print(
        f"Failed to replace audio in {in_vid_mp4} with {in_mp3} to {out_mp3}, doing re-encode"
    )
    cmd = f'static_ffmpeg -y -i "{in_vid_mp4}" -i "{in_mp3}" {video_stmt} -map 1:a -c:v copy -c:a aac -b:a 320k "{out_mp3}"'
    os.system(cmd)


def strip_ext(path: str) -> str:
    return os.path.splitext(path)[0]


def audnorm(path: str, out: str) -> None:
    """
    Normalizes the audio of a video file.
    """
    assert _is_media_file(path), f"{path} is not a media file"
    if len(os.path.dirname(out)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    add_paths(weak=True)
    add_paths_sox(weak=True)
    # file without extensions
    out_no_ext = strip_ext(out)
    out_wav = f"{out_no_ext}.wav"
    out_wav_norm = f"{out_no_ext}_norm.wav"
    out_m4a = f"{out_no_ext}.m4a"
    _convert_to_wav(path, out_wav)

    sox_cmd = f'static_sox "{out_wav}" "{out_wav_norm}" norm'
    print(f"Executing:\n  {sox_cmd}")
    os.system(sox_cmd)
    # Note that aac is supported by twitter, lame is not.
    # cmd = f'ffmpeg-normalize -f "{path}" -o "{out}" -c:a aac -b:a 192k'
    # print(f"Executing:\n  {cmd}")
    _convert_to_mp3(out_wav_norm, out_m4a)

    # now mix in new audio with old video
    _replace_audio(in_vid_mp4=out_m4a, in_mp3=path, out_mp3=out)


def main():
    """Main entry point for audnorm."""
    parser = argparse.ArgumentParser(
        description="Print video durations\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("vidfile", help="Path to vid file", nargs="?")
    parser.add_argument("out", help="Path to vid file", nargs="?")
    args = parser.parse_args()
    path = args.vidfile or input("in vid file: ")
    out = args.out or input("out vid file: ")
    if len(os.path.dirname(out)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    audnorm(path, out)


if __name__ == "__main__":
    main()
