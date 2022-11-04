"""
Generates a list of the top directories and files that are taking up space.
The search is started from the cwd.
"""
# pylint: skip-file

import argparse
import os
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Any, Dict, List


# signal handler for ctrl-c
def handle_ctrlc(sig, frame):  # pylint: disable=unused-argument
    print("Disk audit cancelled")
    sys.exit(0)


def add_path(tree: dict, path_list: List[str], size: int) -> None:
    curr_tree: dict = tree
    for p in path_list:
        curr_tree["size"] += size
        subtree = curr_tree["children"].get(p, None)
        if subtree is None:
            subtree = dict(name=p, size=size, children={})
            curr_tree["children"][p] = subtree
        curr_tree = subtree
    curr_tree["size"] += size


def split_paths(path: str) -> List[str]:
    out: List = []
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


def get_size_runner(inqueue: Queue, outqueue: Queue) -> None:
    count = 0
    while not inqueue.empty():
        try:
            fullpath = inqueue.get()
            try:
                size = os.path.getsize(fullpath)
            except FileNotFoundError:
                continue
            except OSError:
                continue
            outqueue.put((fullpath, size))
            count += 1
            if count % 1000 == 0:
                time.sleep(0.001)
                count = 0
        except KeyboardInterrupt:
            handle_ctrlc(None, None)


def main() -> None:
    signal.signal(signal.SIGINT, handle_ctrlc)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    # threading queue
    inque: Queue = Queue()
    scan_start_time = time.time()
    if args.verbose:
        print("Scanning files...")
    for root, _, files in os.walk(".", topdown=True):
        for name in files:
            fullpath = os.path.join(root, name)
            inque.put(fullpath)
    scan_diff = time.time() - scan_start_time
    size_start_time = time.time()
    tree: Dict[str, Any] = dict(name="root", size=0, children={})
    outque: Queue = Queue()
    tasks = []
    if args.verbose:
        print("Calculating file sizes...")
    with ThreadPoolExecutor(max_workers=16) as executor:
        task = executor.submit(get_size_runner, inque, outque)
        tasks.append(task)
    [task.result() for task in tasks]
    # get_size_runner(inqueue, outque)
    if args.verbose:
        print("Partitioning results...")
    while not outque.empty():
        fullpath, size = outque.get()
        path_lst = split_paths(fullpath)
        add_path(tree, path_lst, size)
    size_diff = time.time() - size_start_time

    partion_sort_start_time = time.time()
    top: dict = tree["children"]["."]
    top_sizes = []
    total_size = 0
    for _, node in top["children"].items():
        n = node["size"]
        total_size += n
        top_sizes.append((n, node["name"]))
    top_sizes.sort()
    top_sizes.reverse()
    max_nm_len = 0
    for _, name in top_sizes:
        if len(name) > max_nm_len:
            max_nm_len = len(name)
    lines = [f"Total size: {fmt_num(total_size)}:"]
    for size, name in top_sizes:
        nm = name + ": ".ljust(max_nm_len + 2 - len(name), " ")
        perc_num = "{:.1%}".format(size / total_size)
        if os.path.isfile(name):
            nm = "F " + nm
        else:
            nm = "D " + nm
        num = fmt_num(size)
        lines.append(f"  {nm} {num} ({perc_num})")
    partion_sort_diff = time.time() - partion_sort_start_time

    print("\n".join(lines))
    total_time = time.time() - scan_start_time
    if args.verbose:
        print(f"Completed in: {total_time:.1f} seconds")
        print(f"  Scan time: {scan_diff:.1f} seconds")
        print(f"  Size time: {size_diff:.1f} seconds")
        print(f"  Sort time: {partion_sort_diff:.1f} seconds")


if __name__ == "__main__":
    main()
    sys.exit(0)
