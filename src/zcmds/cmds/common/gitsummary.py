"""
Returns a git summary of the current directory.
"""


import os
import subprocess
import sys
from argparse import Action, ArgumentParser
from datetime import datetime, timedelta


def create_cmd(start_date: datetime, end_date: datetime) -> str:
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    cmd = f'git log --since="{start_date_str}" --until="{end_date_str}" --pretty="format:%h %ad %s" --date=local --reverse'
    return cmd


def check_date(date: str) -> bool:
    # Makes sure that the date is in the correct format
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


class OutputAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, "DEFAULT_GIT_SUMMARY_OUTPUT")
        else:
            setattr(namespace, self.dest, values)


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
        # print(line)
        (month, day, _time, year) = line.split(" ", 6)[2:6]
        dtime: datetime = datetime.strptime(
            f"{month} {day} {year} {_time}", "%b %d %Y %H:%M:%S"
        )

        if dtime >= start_date and dtime < end_date:  # type: ignore
            out.append(line)
    return "\n".join(out)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--start_date", help="First page to include in the output.")
    parser.add_argument(
        "--end_date", help="Last page (inclusive) to include in the output."
    )
    # add header
    parser.add_argument(
        "--no-header",
        help="Suppresses the header",
    )
    parser.add_argument(
        "--output",
        nargs="?",
        default="DEFAULT_GIT_SUMMARY_OUTPUT",
        action=OutputAction,
        help="Output file, if not specified, will print to stdout",
    )
    args = parser.parse_args()

    start_date = args.start_date or input("start_date [YYYY-MM-DD]: ")
    if not check_date(start_date):
        sys.stderr.write("Error: Incorrect date format, should be YYYY-MM-DD\n")
        sys.exit(1)
    end_date = args.end_date or input("end_date [YYYY-MM-DD]: ")
    if not check_date(end_date):
        sys.stderr.write("Error: Incorrect date format, should be YYYY-MM-DD\n")
        sys.exit(1)
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    cmd = create_cmd(start_date_dt - timedelta(days=1), end_date_dt + timedelta(days=1))
    sys.stderr.write(f"Running: {cmd}\n")
    cp: subprocess.CompletedProcess = subprocess.run(
        cmd, shell=True, check=True, capture_output=True, universal_newlines=True
    )
    stdout = cp.stdout.strip()
    stdout = constrain(stdout, start_date_dt, end_date_dt)

    repo_url = get_repo_url()

    if not args.no_header:
        header = f"Git summary for {repo_url} from {start_date} to {end_date}\n------------------\n"
        stdout = header + stdout

    if not args.output:
        print(stdout)
    else:
        output = args.output
        if output == "DEFAULT_GIT_SUMMARY_OUTPUT":
            curr_dir = os.path.basename(os.path.abspath(os.getcwd()))
            output = f"summary_{curr_dir.replace('/', '_').replace(':', '_')}_{start_date}_{end_date}.txt"
        with open(output, encoding="utf-8", mode="w") as f:
            f.write(stdout)
        print(f"Output written to {output}")

    sys.exit(0)


if __name__ == "__main__":
    sys.argv.append("--output")
    main()
