"""
    Downloads and clips videos from youtube, rumble, bitchute (using yt-dlp) and clips
    the video using ffmpeg.
"""


import subprocess
import os
import time
import sys
from typing import Optional, Tuple

from concurrent.futures import ThreadPoolExecutor


def _find_video_file_from_stdout(stdout: str) -> Optional[str]:
    value = None
    for line in stdout.splitlines():
        # File pattern # 1
        needle = '[Merger] Merging formats into "'
        if needle in line:
            value = line.replace(needle, "").replace('"', "")
            continue
        # File pattern # 2 (found in brighteon)
        needle = "[download] Destination: "
        if needle in line:
            value = line.replace(needle, "")
            continue
    return value


def _exec(cmd_str: str) -> Tuple[int, str, str]:
    proc_yt = subprocess.Popen(
        cmd_str,
        shell=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc_yt.communicate()
    assert proc_yt.returncode is not None
    return proc_yt.returncode, stdout, stderr


def run_download_and_cut(url, outname, start_timestamp, length):
    # Run yt-dlp task, --no-check-certificate is needed for rumble and
    # possibly others.
    yt_dlp_cmd: str = f"yt-dlp --no-check-certificate --force-overwrites {url}"
    returncode, stdout, stderr = _exec(yt_dlp_cmd)
    # Search through the output of the yt-dlp command to for the
    # file name.
    fullvideo = _find_video_file_from_stdout(stdout + stderr)
    if fullvideo is None:
        raise OSError(
            f"Could not find a video in \n"
            "###################\n"
            f"{stdout}"
            "\n###################\n"
            f"with command '{yt_dlp_cmd}'\n"
            f"RETURNED: {returncode}\n"
        )
    ffmpeg_cmd = (
        f'ffmpeg -y -i "{fullvideo}"'  # accepts any prompts with y
        # start timestamp (seconds or h:mm:ss:ff)
        f" -ss {start_timestamp}"
        # length timestamp (seconds or h:mm:ss:ff)
        f" -t {length}"
        f" {outname}.mp4"
    )
    returncode, stdout, stderr = _exec(ffmpeg_cmd)
    if returncode != 0:
        raise OSError(
            f"Error running {ffmpeg_cmd}."
            "###################\n"
            f"STDOUT:\n{stdout}\n"
            "\n###################\n"
            f"STDERR:\n{stderr}\n"
            "\n###################\n"
            f"with command '{yt_dlp_cmd}'\n"
        )
    os.remove(fullvideo)


def _finish_then_print_completion(future):
    try:
        future.result()
        print(f'Finished job "{future.url}"')
    except BaseException as be:
        print(f'ERROR fetching clip from "{future.url}" because of error:\n' f"{be}\n")


def unit_test_brighteon():
    run_download_and_cut(
        "https://www.brighteon.com/f596cc8b-4b52-4152-92cb-39dadc552833",
        "health_ranger_report",
        "10:47",
        "20",
    )


def main():
    futures = []
    executor = ThreadPoolExecutor(max_workers=8)
    try:
        while True:
            print("Add new video:")
            url = input("  url: ")
            start_timestamp = input("  start_timestamp: ")
            length = input("  length: ")
            output_name = input("  output_name: ")

            def task():
                return run_download_and_cut(url, output_name, start_timestamp, length)

            f = executor.submit(task)
            setattr(f, "url", url)
            futures.append(f)
            print(f"\nStarting {url} in background.\n")
            # Have any futures completed?
            finished_futures = [f for f in futures if f.done()]
            futures = [f for f in futures if f not in finished_futures]
            for f in finished_futures:
                _finish_then_print_completion(f)

    except KeyboardInterrupt:
        print("\n\n")
        pass

    unfinished_futures = [f for f in futures if not f.done()]
    if unfinished_futures:
        print(f"Waiting for {len(unfinished_futures)} commands to finish")
        for i, f in enumerate(unfinished_futures):
            sys.stdout.write(f"  Waiting for {f.url} to finish...\n")
            while not f.done():
                time.sleep(0.1)
            _finish_then_print_completion(f)
            sys.stdout.write(f"  ... done, {len(unfinished_futures)-i} left\n")
    print("All commands completed.")


if __name__ == "__main__":
    # unit_test_brighteon()
    main()
