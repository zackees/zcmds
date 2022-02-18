import subprocess
import os
import time
import sys

from concurrent.futures import ThreadPoolExecutor


def run_download_and_cut(url, outname, start_timestamp, length):
    stdout = subprocess.check_output(
        f'yt-dlp --no-check-certificate --force-overwrites {url}', shell=True, universal_newlines=True, stderr=subprocess.PIPE)
    value = None
    for line in stdout.splitlines():
        needle = '[Merger] Merging formats into "'
        if needle in line:
            value = line.replace(needle, '').replace('"', '')
            break
    if value is None:
        raise OSError(f"Could not find a video in {stdout}")
    ffmpeg_cmd = f'ffmpeg -y -i "{value}" -ss {start_timestamp} -t {length} {outname}.mp4'
    stdout = subprocess.check_output(
        ffmpeg_cmd, shell=True, universal_newlines=True, stderr=subprocess.PIPE)
    os.remove(value)


def main():
    futures = []
    executor = ThreadPoolExecutor(max_workers=8)
    try:
        while True:
            print("Add new video:")
            url = input('  url: ')
            start_timestamp = input('  start_timestamp: ')
            length = input('  length: ')
            output_name = input('  output_name: ')

            def task(): return run_download_and_cut(
                url, output_name, start_timestamp, length)
            f = executor.submit(task)
            setattr(f, 'url', url)
            futures.append(f)
            print(f"\nStarting {url} in background.\n")
    except KeyboardInterrupt:
        pass

    unfinished_futures = [f for f in futures if not f.done()]
    if unfinished_futures:
        print(f"\nWaiting for {len(unfinished_futures)} commands to finish")
        for i, f in enumerate(unfinished_futures):
            sys.stdout.write(f"  Waiting for {f.url} to finish...\n")
            while not f.done():
                time.sleep(.1)
            sys.stdout.write(f"  ... done, {len(unfinished_futures)-i} left\n")

    print("All commands successfully completed.")


if __name__ == "__main__":
    main()
