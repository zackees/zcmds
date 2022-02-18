import subprocess
import re

def validate(timestamp):
    return True
    


def make_cmd(url, start_timestamp, end_timestamp):
    return f'yt-dlp -f "(bestvideo+bestaudio/best)[protocol!*=dash]" --external-downloader ffmpeg --external-downloader-args "ffmpeg_i:-ss {start_timestamp} -to {end_timestamp}" "{url}"'


def queue_download_and_cut():
    url = input("Url: ")
    while True:
        start_time = input("Start Timestamp: ")
        if validate(start_time):
            break
    while True:
        end_time = input("End Timestamp: ")
        if validate(end_time):
            break
    cmd = make_cmd(url, start_time, end_time)
    print(cmd)
    p = subprocess.Popen(cmd, shell=True, universal_newlines=True)
    return p


def main():
    procs = []
    while True:
        try:
            p = queue_download_and_cut()
            procs.append(p)
        except KeyboardInterrupt:
            break

    for p in procs:
        p.wait()


if __name__ == "__main__":
    main()
