"""Download .ts (transport stream) segments from a base URL."""

import _thread
import concurrent.futures
import logging
import os
import sys
import threading
import time
import warnings

import httpx  # type: ignore


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("tsdownloader.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)

START_NUM = 1
MAX_WORKERS = 8
DEST_FOLDER = "out"
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0  # seconds
ERRORS: list[str] = []
START_EPOCH: float = 0.0
SHUTDOWN_EVENT = threading.Event()


def get_timestamp() -> str:
    """Get elapsed time since start as formatted string."""
    elapsed = time.time() - START_EPOCH
    return f"[{elapsed:7.1f}]"


def make_url(base_url: str, ts_index: int) -> str:
    """Generate a .ts segment URL from the base URL and index."""
    return f"{base_url}index_1_{ts_index:05d}.ts"


def check_url(client: httpx.Client, url: str) -> bool:
    """Check if a URL is accessible using httpx client with connection pooling."""
    retries = 10
    while retries > 0 and not SHUTDOWN_EVENT.is_set():
        retries -= 1
        try:
            response = client.head(url)
            if response.status_code == 200:
                return True
        except KeyboardInterrupt:
            logger.info("check_url interrupted by user")
            SHUTDOWN_EVENT.set()
            _thread.interrupt_main()
            return False
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error for {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in check_url for {url}: {e}")
    return False


def download(url: str) -> None:
    """Download a .ts segment using httpx with retry logic and exponential backoff."""
    # Check shutdown flag before starting
    if SHUTDOWN_EVENT.is_set():
        return

    filename = url.split("/")[-1]
    dest_path = os.path.join(DEST_FOLDER, filename)

    try:
        if os.path.exists(dest_path):
            if not SHUTDOWN_EVENT.is_set():
                print(f"{get_timestamp()} File already exists: {dest_path}")
            return

        # Retry loop with exponential backoff
        for attempt in range(MAX_RETRIES):
            if SHUTDOWN_EVENT.is_set():
                return

            try:
                # Download using httpx with streaming
                with httpx.stream("GET", url, timeout=30.0) as response:
                    response.raise_for_status()

                    # Write to file in chunks
                    with open(dest_path, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            if SHUTDOWN_EVENT.is_set():
                                # Stop downloading if shutdown is requested
                                break
                            f.write(chunk)

                # Only print success if shutdown wasn't requested
                if not SHUTDOWN_EVENT.is_set():
                    if attempt > 0:
                        print(
                            f"{get_timestamp()} Downloaded: {filename} (after {attempt + 1} attempts)"
                        )
                    else:
                        print(f"{get_timestamp()} Downloaded: {filename}")
                return  # Success! Exit the retry loop

            except httpx.HTTPStatusError as e:
                # Don't retry on 4xx errors (except 408 Request Timeout and 429 Too Many Requests)
                status_code = e.response.status_code
                if 400 <= status_code < 500 and status_code not in [408, 429]:
                    if not SHUTDOWN_EVENT.is_set():
                        warning_msg = f"HTTP error downloading {url}: {status_code} (not retrying)"
                        logger.error(warning_msg)
                        warnings.warn(warning_msg)
                        ERRORS.append(warning_msg)
                    # Clean up partial download
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    return  # Don't retry on client errors

                # Retry on 5xx errors, 408, 429
                if attempt < MAX_RETRIES - 1:
                    backoff_time = INITIAL_BACKOFF * (2**attempt)
                    if not SHUTDOWN_EVENT.is_set():
                        logger.warning(
                            f"HTTP error {status_code} downloading {url}, retrying in {backoff_time:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})"
                        )
                    time.sleep(backoff_time)
                    # Clean up partial download before retry
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                else:
                    # Final attempt failed
                    if not SHUTDOWN_EVENT.is_set():
                        warning_msg = f"HTTP error downloading {url}: {status_code} (failed after {MAX_RETRIES} attempts)"
                        logger.error(warning_msg)
                        warnings.warn(warning_msg)
                        ERRORS.append(warning_msg)
                    # Clean up partial download
                    if os.path.exists(dest_path):
                        os.remove(dest_path)

            except (
                httpx.TimeoutException,
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ) as e:
                # Retry on transient network errors
                if attempt < MAX_RETRIES - 1:
                    backoff_time = INITIAL_BACKOFF * (2**attempt)
                    if not SHUTDOWN_EVENT.is_set():
                        logger.warning(
                            f"Network error downloading {url}: {e}, retrying in {backoff_time:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})"
                        )
                    time.sleep(backoff_time)
                    # Clean up partial download before retry
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                else:
                    # Final attempt failed
                    if not SHUTDOWN_EVENT.is_set():
                        warning_msg = f"Network error downloading {url}: {e} (failed after {MAX_RETRIES} attempts)"
                        logger.error(warning_msg)
                        warnings.warn(warning_msg)
                        ERRORS.append(warning_msg)
                    # Clean up partial download
                    if os.path.exists(dest_path):
                        os.remove(dest_path)

    except KeyboardInterrupt:
        logger.info("download interrupted by user")
        SHUTDOWN_EVENT.set()
        # Clean up partial download
        if os.path.exists(dest_path):
            os.remove(dest_path)
        _thread.interrupt_main()
    except Exception as e:
        if not SHUTDOWN_EVENT.is_set():
            warning_msg = f"Unexpected error downloading {url}: {e}"
            logger.error(warning_msg)
            warnings.warn(warning_msg)
            ERRORS.append(warning_msg)
        # Clean up partial download
        if os.path.exists(dest_path):
            os.remove(dest_path)


def main() -> int:
    """
    Download .ts segments from a base URL.

    Usage:
        tsdownloader [start_time]

    Arguments:
        start_time: Optional epoch time to use as reference (default: current time)

    Prompts the user for the base URL and downloads all available segments.
    """
    global START_EPOCH

    try:
        # Get start time from argument or use current time
        if len(sys.argv) > 1:
            try:
                START_EPOCH = float(sys.argv[1])
            except ValueError:
                print(
                    f"{get_timestamp()} Error: Invalid time value '{sys.argv[1]}'",
                    file=sys.stderr,
                )
                return 1
        else:
            START_EPOCH = time.time()

        # Prompt user for base URL
        print(f"{get_timestamp()} Enter the base URL for .ts segments:")
        print(
            f"{get_timestamp()} Example: https://example.com/hls/live/12345/stream/master/"
        )
        base_url = input("Base URL: ").strip()

        if not base_url:
            print(f"{get_timestamp()} Error: Base URL cannot be empty", file=sys.stderr)
            return 1

        # Ensure base URL ends with /
        if not base_url.endswith("/"):
            base_url += "/"

        # Create the destination folder if it doesn't exist
        if not os.path.exists(DEST_FOLDER):
            os.makedirs(DEST_FOLDER)

        print(f"{get_timestamp()} Downloading .ts segments to: {DEST_FOLDER}")
        print(f"{get_timestamp()} Using base URL: {base_url}")

        # Create httpx client with connection pooling and HTTP/2 support
        with httpx.Client(timeout=5.0, http2=True) as client:
            # Create a ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=MAX_WORKERS
            ) as executor:
                ts_index = START_NUM
                while not SHUTDOWN_EVENT.is_set():
                    url = make_url(base_url, ts_index)
                    filename = url.split("/")[-1]
                    dest_path = os.path.join(DEST_FOLDER, filename)

                    # Check if file exists locally first (fast)
                    if os.path.exists(dest_path):
                        elapsed = time.time() - START_EPOCH
                        print(
                            f"[{elapsed:7.1f}] Segment {ts_index} already exists, skipping..."
                        )
                        ts_index += 1
                        continue

                    # Only check remote URL if file doesn't exist locally
                    if not check_url(client, url):
                        elapsed = time.time() - START_EPOCH
                        print(
                            f"\n[{elapsed:7.1f}] No more segments found. Last segment: index_1_{ts_index - 1:05d}.ts"
                        )
                        break

                    elapsed = time.time() - START_EPOCH
                    print(f"[{elapsed:7.1f}] Downloading segment {ts_index}...")
                    executor.submit(download, url)
                    ts_index += 1

                # Wait for all futures to complete
                executor.shutdown(wait=not SHUTDOWN_EVENT.is_set())

        # Print all errors at the end
        if ERRORS and not SHUTDOWN_EVENT.is_set():
            print("\nEncountered Errors:")
            for error in ERRORS:
                print(f"{get_timestamp()} {error}")
            return 1

        elapsed = time.time() - START_EPOCH
        print(
            f"\n[{elapsed:7.1f}] Download complete! Total segments: {ts_index - START_NUM}"
        )
        return 0

    except KeyboardInterrupt:
        logger.info("main interrupted by user")
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"{get_timestamp()} Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
