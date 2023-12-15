"""Work in progress"""

import concurrent.futures
import os
import sys
import warnings

import requests  # type: ignore

BASE_URL = "https://www-senate-gov-media-srs.akamaized.net/hls/live/2036788/judiciary/judiciary121323p/master/"
START_NUM = 1
MAX_WORKERS = 8
DEST_FOLDER = "out"
ERRORS = []

# Create the destination folder if it doesn't exist
if not os.path.exists(DEST_FOLDER):
    os.makedirs(DEST_FOLDER)


def make_url(ts_index: int) -> str:
    return f"{BASE_URL}index_1_{ts_index:05d}.ts"


def check_url(url: str) -> bool:
    retries = 10
    while retries > 0:
        retries -= 1
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException as e:
            warnings.warn(f"Request exception for {url}: {e}")
    return False


def download(url: str) -> None:
    try:
        filename = url.split("/")[-1]
        dest_path = os.path.join(DEST_FOLDER, filename)
        if not os.path.exists(dest_path):  # Check if the file already exists
            os.system(f'aria2c -d "{DEST_FOLDER}" -o "{filename}" "{url}"')
        else:
            print(f"File already exists: {dest_path}")
    except Exception as e:
        warning_msg = f"Error downloading {url}: {e}"
        warnings.warn(warning_msg)
        ERRORS.append(warning_msg)


def main() -> int:
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        ts_index = START_NUM
        while True:
            url = make_url(ts_index)
            if not check_url(url):
                break

            executor.submit(download, url)
            ts_index += 1

        # Wait for all futures to complete
        executor.shutdown(wait=True)

    # Print all errors at the end
    if ERRORS:
        print("\nEncountered Errors:")
        for error in ERRORS:
            print(error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
