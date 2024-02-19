"""
Returns a git summary of the current directory.
"""

import json
import os
import subprocess
import sys
from argparse import Action, ArgumentParser
from collections import OrderedDict
from datetime import datetime, timedelta

from zcmds.util.config import get_config, save_config

CONFIG_NAME = "gitsummary.json"


class OutputAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None and option_string is None:
            setattr(namespace, self.dest, None)
        elif values is None:
            setattr(namespace, self.dest, "DEFAULT_GIT_SUMMARY_OUTPUT")
        else:
            setattr(namespace, self.dest, values)


def create_cmd(start_date: datetime, end_date: datetime) -> str:
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    cmd = (
        f'git log --since="{start_date_str}"'
        f' --until="{end_date_str}"'
        ' --pretty="format:%h %ad %s"'
        " --date=local --reverse"
    )
    return cmd


def check_date(date: str) -> bool:
    # Makes sure that the date is in the correct format
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_repo_url() -> str:
    # git config --get remote.origin.url
    cp: subprocess.CompletedProcess = subprocess.run(
        "git config --get remote.origin.url",
        shell=True,
        check=True,
        capture_output=True,
        universal_newlines=True,
    )
    return cp.stdout.strip()


def constrain(output: str, start_date: datetime, end_date: datetime) -> str:
    lines = output.strip().splitlines()
    out = []
    for line in lines:
        (month, day, _time, year) = line.split(" ", 6)[2:6]
        dtime: datetime = datetime.strptime(
            f"{month} {day} {year} {_time}", "%b %d %Y %H:%M:%S"
        )
        if dtime >= start_date and dtime < end_date:  # type: ignore
            out.append(line)
    return "\n".join(out)


def parse_to_json_data(
    repo_url: str, start_date: datetime, end_date: datetime, lines: list[str]
) -> OrderedDict:
    out = OrderedDict()
    data: list[OrderedDict] = []
    # subtract one second
    end_date = end_date - timedelta(seconds=1)
    header = {
        "repo_url": repo_url,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "num_commits": len(lines),
    }
    out["header"] = header
    for line in lines:
        (hash, _, month, day, _time, year, *rest) = line.split(" ")
        rest = " ".join(rest)  # type: ignore
        # print(rest)
        dtime: datetime = datetime.strptime(
            f"{month} {day} {year} {_time}", "%b %d %Y %H:%M:%S"
        )
        item = OrderedDict()
        item["commit"] = hash
        item["date_time"] = dtime.isoformat()
        item["message"] = rest  # type: ignore
        data.append(item)
    out["data"] = data  # type: ignore
    return out


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("repo", help="Path to the repo to summarize", nargs="?")
    parser.add_argument("--start_date", help="First page to include in the output.")
    parser.add_argument(
        "--end_date", help="Last page (inclusive) to include in the output."
    )
    parser.add_argument(
        "--output",
        help="Output file.",
    )
    parser.add_argument("--json", help="Output in JSON format", action="store_true")
    args = parser.parse_args()
    if args.output:
        ext = os.path.splitext(args.output)[1]
        if args.json and ext != ".json" and args.output != "stdout":
            sys.stderr.write("Error: Output file must be a .json file\n")
            return 1
        if ext == ".json" and not args.json:
            args.json = True
    if args.output != "stdout" and args.output is not None:
        args.output = os.path.abspath(args.output)
    config = get_config(CONFIG_NAME)
    start_date = args.start_date
    if not start_date:
        saved_start_date = config.get("start_date") or "YYYY-MM-DD"
        start_date = input(f"start_date [{saved_start_date}]: ").strip()
        if not start_date:
            start_date = saved_start_date
        config["start_date"] = start_date
    if not check_date(start_date):
        sys.stderr.write("Error: Incorrect date format, should be YYYY-MM-DD\n")
        return 1
    end_date = args.end_date
    if not end_date:
        saved_end_date = config.get("end_date") or "YYYY-MM-DD"
        end_date = input(f"end_date [{saved_end_date}]: ").strip()
        if not end_date:
            end_date = saved_end_date
        config["end_date"] = end_date
    if not check_date(end_date):
        sys.stderr.write("Error: Incorrect date format, should be YYYY-MM-DD\n")
        return 1
    repo = ""
    if not args.repo:
        repo = os.getcwd()
        if not os.path.isdir(repo):
            sys.stderr.write(f"Error: {repo} is not a directory\n")
            sys.exit(1)
    else:
        repo = args.repo
        if not os.path.isdir(repo):
            sys.stderr.write(f"Error: {repo} is not a directory\n")
            sys.exit(1)
    os.chdir(repo)
    if not os.path.exists(".git"):
        sys.stderr.write(f"Error: {repo} is not a git repo\n")
        sys.exit(1)
    if 0 != os.system("git status"):
        sys.stderr.write(
            f"Error: {repo} has a .git dir but is not a valid git repo (corrupted?)\n"
        )
        sys.exit(1)
    save_config(CONFIG_NAME, config)
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    repo = ""
    cmd = create_cmd(start_date_dt - timedelta(days=1), end_date_dt + timedelta(days=1))
    sys.stderr.write(f"Running: {cmd}\n")
    cp: subprocess.CompletedProcess = subprocess.run(
        cmd, shell=True, check=True, capture_output=True, universal_newlines=True
    )
    stdout = cp.stdout.strip()
    stdout = constrain(stdout, start_date_dt, end_date_dt)
    repo_url = get_repo_url()
    nlines = len(stdout.splitlines())

    curr_dir = os.path.basename(os.path.abspath(os.getcwd()))
    ext = ".txt" if not args.json else ".json"

    def write_output(data: str) -> None:
        data = data + "\n"
        if args.output == "stdout":
            sys.stdout.write(data)
            return
        if args.output is not None:
            with open(args.output, encoding="utf-8", mode="w") as f:
                f.write(data)
            print(f"Output written to {args.output}")
            return
        output = (
            args.output
            or f"summary_{curr_dir.replace('/', '_').replace(':', '_')}_{start_date}_{end_date}{ext}"
        )
        with open(output, encoding="utf-8", mode="w") as f:
            f.write(data)
            print(f"Output written to {output}")

    if not args.json:
        header = f"Git summary for {repo_url} from {start_date} to {end_date}, {nlines} commits\n------------------"
        write_output(header + "\n" + stdout)
        return 0
    data = parse_to_json_data(repo_url, start_date_dt, end_date_dt, stdout.splitlines())
    json_str = json.dumps(data, indent=4)
    write_output(json_str)
    return 0


def unit_test() -> None:
    # "C:\Users\niteris\dev\Accessibility-Test-Framework-for-Android" --start_date 2023-11-15 --end_date 2023-11-30 --output "gitsummary\2023-11-15_2023-11-30\Accessibility-Test-Framework-for-Android.json"
    args = [
        r"C:\Users\niteris\dev\Accessibility-Test-Framework-for-Android",
        "--output",
        "out.json",
        "--start_date",
        "2023-01-01",
        "--end_date",
        "2023-01-31",
    ]
    sys.argv.extend(args)
    rtn = main()
    sys.exit(rtn)


if __name__ == "__main__":
    unit_test()
