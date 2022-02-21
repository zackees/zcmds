"""
Generates a list of the top directories and files that are taking up space.
The search is started from the cwd.
"""
# pylint: skip-file


import os
import sys
from typing import Any, Dict, List


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


def main() -> None:
    tree: Dict[str, Any] = dict(name="root", size=0, children={})
    for root, _, files in os.walk(".", topdown=True):
        split_paths(root)
        for name in files:
            fullpath = os.path.join(root, name)
            try:
                size = os.path.getsize(fullpath)
                path_lst = split_paths(fullpath)
                add_path(tree, path_lst, size)
            except FileNotFoundError:
                continue
            except OSError:
                continue

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
    print("\n".join(lines))


if __name__ == "__main__":
    main()
    sys.exit(0)
