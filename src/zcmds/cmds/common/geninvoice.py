# pylint: disable=broad-exception-raised


import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List, Tuple

import json5 as json  # type: ignore


@dataclass
class DateRange:
    start_date: datetime
    end_date: datetime

    def to_json(self) -> list[str]:
        a = self.start_date.strftime("%Y-%m-%d")
        b = self.end_date.strftime("%Y-%m-%d")
        return [b, a]

    @staticmethod
    def from_json(data: List[str]) -> "DateRange":
        b, a = data[:2]
        b_dt = datetime.strptime(b, "%Y-%m-%d")
        a_dt = datetime.strptime(a, "%Y-%m-%d")
        return DateRange(a_dt, b_dt)

    def __iter__(self) -> Generator[Tuple[datetime, datetime], None, None]:
        yield (self.start_date, self.end_date)


def write_utf8(filename: str, content: str) -> None:
    with open(filename, encoding="utf-8", mode="w") as filed:
        filed.write(content)


def read_utf8(filename: str) -> str:
    with open(filename, encoding="utf-8", mode="r") as filed:
        return filed.read()


@dataclass
class Config:
    dates: List[DateRange]
    repos: List[str]

    def to_json(self) -> Dict[str, Any]:
        # recursively convert to json
        out = {}
        out["dates"] = [date.to_json() for date in self.dates]
        out["repos"] = self.repos  # type: ignore
        return out

    def to_json_str(self) -> str:
        data = self.to_json()
        return json.dumps(data, indent=4)

    @staticmethod
    def from_json(json_str: str) -> "Config":
        data = json.loads(json_str)
        dates = [DateRange.from_json(date) for date in data["dates"]]
        repos = data["repos"]
        return Config(dates=dates, repos=repos)

    def save(self, filename: str) -> None:
        write_utf8(filename, self.to_json_str())

    @staticmethod
    def load(filename: str) -> "Config":
        return Config.from_json(read_utf8(filename))


def find_folders_with_git_repos(cur_dir: str) -> list[str]:
    """Returns a list of folders that contain git repos."""
    folders = []
    depth = 2
    for root, dirs, _ in os.walk(cur_dir):
        if ".git" in dirs:
            folders.append(os.path.abspath(root))
        if root.count(os.sep) >= depth:
            del dirs[:]
    return folders


def last_month_dates(num_months: int, now: datetime) -> List[DateRange]:
    """Returns a list of DateRange objects for the last num_months months."""
    out: List[DateRange] = []

    for i in range(num_months):
        month_start = now - timedelta(days=30 * i)
        current_month = month_start.month
        first_day = datetime(month_start.year, current_month, 1)
        mid_day = datetime(month_start.year, current_month, 15)
        next_month = current_month + 1
        year = month_start.year
        if next_month > 12:
            next_month = 1
            year += 1

        last_day = datetime(year, next_month, 1) - timedelta(days=1)

        # Only add date ranges that are not in the future
        if last_day <= now:
            out.append(DateRange(mid_day, last_day))
        if mid_day <= now:
            out.append(DateRange(first_day, mid_day))

    return out


def edit_text_file(filename: str) -> None:
    # blocking call to open file, wait for it to close
    if sys.platform == "win32":
        os.system(f'notepad.exe "{filename}"')
    else:
        editors = ["pico", "nano"]
        for editor in editors:
            if shutil.which(editor):
                os.system(f"{editor} {filename}")
                return
        raise Exception(f"Could not find any of the editors: {editors}")


def main() -> None:
    config_file = "genvoice.json"
    if not os.path.exists(config_file):
        print(f"Config file {config_file} does not exist.")
        dates = last_month_dates(2, now=datetime.now())
        repos = find_folders_with_git_repos(".")
        new_config = Config(dates=dates, repos=repos)
        new_config.save(config_file)

    edit_text_file(config_file)
    config = Config.load(config_file)
    print(config.to_json_str())

    if os.path.exists("gitsummary"):
        # clear all contents in folder, but keep the root folder
        for filename in os.listdir("gitsummary"):
            item = os.path.join("gitsummary", filename)
            if os.path.isfile(item):
                os.remove(item)
            else:
                shutil.rmtree(os.path.join("gitsummary", filename))

    all_content_text: list[str] = []
    for date_range in config.dates:
        # start_date, end_date = date_range.start_date.strftime(
        #    "%Y-%m-%d"
        # ), date_range.end_date.strftime("%Y-%m-%d")
        start_date = date_range.start_date.strftime("%Y-%m-%d")
        end_date = date_range.end_date.strftime("%Y-%m-%d")
        folder_name = os.path.join("gitsummary", f"{start_date}_{end_date}")
        commit_count = 0
        content_text: list[str] = []
        for repo in config.repos:
            json_file = os.path.join(folder_name, os.path.basename(repo)) + ".json"
            txt_file = os.path.join(folder_name, os.path.basename(repo)) + ".txt"
            os.makedirs(os.path.dirname(json_file), exist_ok=True)
            for outfile in [json_file, txt_file]:
                if os.path.exists(outfile):
                    os.remove(outfile)
                cmd = f'gitsummary "{repo}" --start_date {start_date} --end_date {end_date} --output "{outfile}"'
                print(f"Running {cmd}")
                os.system(cmd)
            try:
                with open(json_file, encoding="utf-8", mode="r") as f:
                    json_data = json.loads(f.read())
                commit_count += json_data["header"]["num_commits"]
                content_text.append(read_utf8(txt_file))
            except Exception as err:
                print(f"Error: {err}")
                continue

        context_text_str = "\n\n".join(content_text)
        all_content_text.append(context_text_str)
        with open(
            os.path.join(folder_name, "all.txt"), encoding="utf-8", mode="w"
        ) as f:
            f.write(context_text_str)

    all_content_text_str = "\n\n".join(all_content_text)
    with open(os.path.join("gitsummary", "all.txt"), encoding="utf-8", mode="w") as f:
        f.write(all_content_text_str)
    os.system('open "gitsummary"')
    sys.exit(0)


if __name__ == "__main__":
    main()
