import json
import os
import sys
from datetime import datetime

DATES = [
    ("2023-01-16", "2023-01-24"),
    ("2023-01-24", "2023-02-01"),
    ("2023-02-01", "2023-02-08"),
    ("2023-02-08", "2023-02-16"),
    ("2023-02-16", "2023-02-22"),
    ("2023-02-22", "2023-03-01"),
    ("2023-03-01", "2023-03-08"),
    ("2023-03-08", "2023-03-16"),
    ("2023-03-16", "2023-03-24"),
    ("2023-03-24", "2023-04-01"),
]

REPOS: list[str] = [
    # Add your repos here as file paths.
]


def midpoint(start_date: datetime, end_date: datetime) -> datetime:
    return start_date + (end_date - start_date) / 2


def print_dates() -> None:
    for i, _ in enumerate(DATES):
        if i >= len(DATES):
            break
        start_date, end_date = DATES[i]
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        mid_date_dt = midpoint(start_date_dt, end_date_dt)
        start_date_str = start_date_dt.strftime("%Y-%m-%d")
        mid_date_str = mid_date_dt.strftime("%Y-%m-%d")
        end_date_str = end_date_dt.strftime("%Y-%m-%d")
        print(f'("{start_date_str}", "{mid_date_str}"),')
        print(f'("{mid_date_str}", "{end_date_str}"),')


def main() -> None:
    for start_date, end_date in DATES:
        folder_name = os.path.join("gitsummary", f"{start_date}_{end_date}")
        commit_count = 0
        for repo in REPOS:
            os.makedirs(folder_name, exist_ok=True)
            outfile = os.path.join(folder_name, os.path.basename(repo)) + ".json"
            cmd = f'gitsummary "{repo}" --start_date {start_date} --end_date {end_date} --output "{outfile}"'
            with open(outfile, encoding="utf-8", mode="r") as f:
                json_data = json.loads(f.read())
            commit_count += json_data["header"]["num_commits"]
            print(cmd)
            os.system(cmd)
        outname = os.path.join(folder_name, "total_commits.txt")
        os.makedirs(os.path.dirname(outname), exist_ok=True)
        with open(outname, encoding="utf-8", mode="w") as f:
            f.write(str(commit_count))
    sys.exit(0)


if __name__ == "__main__":
    main()
