"""
Generates a list of the top directories and files that are taking up space.
The search is started from the cwd.
"""

# pylint: skip-file

import argparse
import glob
import os
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Lock
from typing import Any, Callable


TOTAL_COUNT = 0
TOTAL_COUNT_LOCK = Lock()

NUM_THREADS = 8


def increment_total_count() -> None:
    global TOTAL_COUNT
    with TOTAL_COUNT_LOCK:
        TOTAL_COUNT += 1


# signal handler for ctrl-c
def handle_ctrlc(sig: int | None, frame: Any) -> None:  # pylint: disable=unused-argument
    print("Disk audit cancelled")
    sys.exit(0)


def add_path(tree: dict[str, Any], path_list: list[str], size: int) -> None:
    curr_tree: dict[str, Any] = tree
    for p in path_list:
        curr_tree["size"] += size
        subtree: dict[str, Any] | None = curr_tree["children"].get(p, None)
        if subtree is None:
            subtree = dict(name=p, size=size, children={})
            curr_tree["children"][p] = subtree
        curr_tree = subtree
    curr_tree["size"] += size


def split_paths(path: str) -> list[str]:
    out: list[str] = []
    curr_path = path
    while True:
        head, leaf = os.path.split(curr_path)
        if leaf == "":
            break
        out.insert(0, leaf)
        if curr_path == head:
            break
        curr_path = head
    return out


def fmt_num(num: int) -> str:
    return "{:,}".format(num)


def get_size_runner(inqueue: Queue[str], outqueue: Queue[tuple[str, int]]) -> None:
    count = 0
    while not inqueue.empty():
        try:
            fullpath: str = inqueue.get()
            try:
                size = os.path.getsize(fullpath)
            except FileNotFoundError:
                continue
            except OSError:
                continue
            outqueue.put((fullpath, size))
            increment_total_count()
            count += 1
            if count % 1000 == 0:
                time.sleep(0.001)
                count = 0
        except KeyboardInterrupt:
            handle_ctrlc(None, None)


def make_filter(globstr: str) -> Callable[[str], bool]:
    """Returns a function that returns True if the path matches the globstr"""
    if globstr == "":
        return lambda _: True

    def match(path: str) -> bool:
        filename = os.path.basename(path)
        return glob.fnmatch.fnmatch(filename, globstr)  # type: ignore

    return match


def main() -> None:
    signal.signal(signal.SIGINT, handle_ctrlc)
    parser = argparse.ArgumentParser(description="Disk audit")
    parser.add_argument("--filter", "-f", help="Filter by file extension", default="")
    args = parser.parse_args()
    # threading queue
    inque: Queue[str] = Queue()
    scan_start_time = time.time()
    print("Scanning for files...")
    matcher_fn = make_filter(args.filter)
    for root, _, files in os.walk(".", topdown=True):
        for name in files:
            fullpath = os.path.join(root, name)
            if matcher_fn(fullpath):
                inque.put(fullpath)
    print(f"  Found {fmt_num(inque.qsize())} files.")
    scan_diff = time.time() - scan_start_time
    size_start_time = time.time()
    tree: dict[str, Any] = dict(name="root", size=0, children={})
    outque: Queue[tuple[str, int]] = Queue()
    tasks: list[Any] = []
    print("Collecting file sizes...")
    executor = ThreadPoolExecutor(max_workers=NUM_THREADS)
    for _ in range(NUM_THREADS):
        task = executor.submit(get_size_runner, inque, outque)
        tasks.append(task)
    print(f"Waiting for {len(tasks)} tasks to complete.")
    [task.result() for task in tasks]
    executor.shutdown()
    # get_size_runner(inqueue, outque)
    print("Partitioning results...")
    partion_sort_start_time = time.time()
    while not outque.empty():
        fullpath, size = outque.get()
        path_lst = split_paths(fullpath)
        add_path(tree, path_lst, size)
    size_diff = time.time() - size_start_time
    top: dict[str, Any] = {}
    if "." in tree["children"]:
        top = tree["children"]["."]
        # ... rest of the code that uses `top`
    else:
        print("No matching files found in the current directory.")
        return
    top_sizes: list[tuple[int, str]] = []
    total_size: int = 0
    for _, node in top["children"].items():
        n: int = node["size"]
        total_size += n
        top_sizes.append((n, node["name"]))
    top_sizes.sort()
    top_sizes.reverse()
    max_nm_len = 0
    for _, name in top_sizes:
        if len(name) > max_nm_len:
            max_nm_len = len(name)

    # lines.append(f"Number of files: {fmt_num(TOTAL_COUNT)}:")
    lines: list[str] = [
        f"Total size: {fmt_num(total_size)}, number of files: {fmt_num(TOTAL_COUNT)}:"
    ]
    for size, name in top_sizes:
        nm: str = name + ": ".ljust(max_nm_len + 2 - len(name), " ")
        perc_num = "{:.1%}".format(size / total_size)
        if os.path.isfile(name):
            nm = "F " + nm
        else:
            nm = "D " + nm
        num = fmt_num(size)
        lines.append(f"  {nm} {num} ({perc_num})")
    partion_sort_diff = time.time() - partion_sort_start_time

    print("\n" + "\n".join(lines))
    total_time = time.time() - scan_start_time
    if total_time > 60:
        total_time_str = f"{total_time / 60:.2f} minutes"
        print(f"\nCompleted in: {total_time_str}")
        print(f"  Scan time: {scan_diff:.1f} seconds")
        print(f"  Size time: {size_diff:.1f} seconds")
        print(f"  Sort time: {partion_sort_diff:.1f} seconds")


if __name__ == "__main__":
    main()
    sys.exit(0)
