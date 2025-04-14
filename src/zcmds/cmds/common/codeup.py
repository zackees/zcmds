"""
Runs:
  * git status
  * if there are not changes then exit 1
  * else
    * if ./lint exists, then run it
    * if ./test exists, then run it
    * git add .
    * aicommit2
"""

import argparse
import os
import subprocess
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Optional

from git import Repo


def is_uv_project(directory=".") -> bool:
    """
    Detect if the given directory is a uv-managed Python project.

    Args:
        directory (str): Path to the directory to check (default is current directory).

    Returns:
        bool: True if it's a uv project, False otherwise.
    """
    try:
        required_files = ["pyproject.toml", "uv.lock"]
        return all(os.path.isfile(os.path.join(directory, f)) for f in required_files)
    except Exception as e:
        print(f"Error: {e}")
        return False


IS_UV_PROJECT = is_uv_project()

# Example usage
if __name__ == "__main__":
    if is_uv_project():
        print("This is a uv project.")
    else:
        print("This is not a uv project.")


def _to_exec_str(cmd: str, bash: bool) -> str:
    if bash and sys.platform == "win32":
        return f"bash -c '{cmd}'"
    return cmd


def _exec(cmd: str, bash: bool, die=True) -> int:
    print(f"Running: {cmd}")
    cmd = _to_exec_str(cmd, bash)
    rtn = os.system(cmd)
    if rtn != 0:
        print(f"Error: {cmd} returned {rtn}")
        if die:
            sys.exit(1)
    return rtn


def find_git_directory() -> str:
    """Traverse up to 3 levels to find a directory with a .git folder."""
    current_dir = os.getcwd()
    for _ in range(3):
        if os.path.exists(os.path.join(current_dir, ".git")):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if current_dir == parent_dir:
            break
        current_dir = parent_dir
    return ""


def check_environment() -> Path:
    if which("git") is None:
        print("Error: git is not installed.")
        sys.exit(1)
    git_dir = find_git_directory()
    if not git_dir:
        print("Error: .git directory does not exist.")
        sys.exit(1)

    if not which("aicommit2"):
        warnings.warn(
            "aicommit2 is not installed. Skipping automatic commit message generation."
        )
    return Path(git_dir)


def get_answer_yes_or_no(question: str, default: Optional[str] = None) -> bool:
    """Ask a yes/no question and return the answer."""
    while True:
        answer = input(question + " [y/n]: ").lower().strip()
        if "y" in answer:
            return True
        if "n" in answer:
            return False
        if answer == "" and default is not None:
            return default == "y"
        print("Please answer 'yes' or 'no'.")


@dataclass
class Args:
    repo: str | None
    no_push: bool
    verbose: bool
    no_test: bool
    no_lint: bool
    publish: bool
    no_autoaccept: bool

    def __post_init__(self) -> None:
        assert isinstance(self.repo, str | None), f"Expected str, got {type(self.repo)}"
        assert isinstance(
            self.no_push, bool
        ), f"Expected bool, got {type(self.no_push)}"
        assert isinstance(
            self.verbose, bool
        ), f"Expected bool, got {type(self.verbose)}"
        assert isinstance(
            self.no_test, bool
        ), f"Expected bool, got {type(self.no_test)}"
        assert isinstance(
            self.no_lint, bool
        ), f"Expected bool, got {type(self.no_lint)}"
        assert isinstance(
            self.publish, bool
        ), f"Expected bool, got {type(self.publish)}"
        assert isinstance(
            self.no_autoaccept, bool
        ), f"Expected bool, got {type(self.no_autoaccept)}"


def _parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Path to the repo to summarize", nargs="?")
    parser.add_argument(
        "--no-push", help="Do not push after successful commit", action="store_true"
    )
    parser.add_argument(
        "--verbose",
        help="Passes the verbose flag to the linter and tester",
        action="store_true",
    )
    parser.add_argument("--publish", "-p", help="Publish the repo", action="store_true")
    parser.add_argument(
        "--no-test", "-nt", help="Do not run tests", action="store_true"
    )
    parser.add_argument("--no-lint", help="Do not run linter", action="store_true")
    parser.add_argument(
        "--no-autoaccept",
        "-na",
        help="Do not auto-accept commit messages from AI",
        action="store_true",
    )
    tmp = parser.parse_args()

    out: Args = Args(
        repo=tmp.repo,
        no_push=tmp.no_push,
        verbose=tmp.verbose,
        no_test=tmp.no_test,
        no_lint=tmp.no_lint,
        publish=tmp.publish,
        no_autoaccept=tmp.no_autoaccept,
    )
    return out


def _publish() -> None:
    publish_script = "upload_package.sh"
    if not os.path.exists(publish_script):
        print(f"Error: {publish_script} does not exist.")
        sys.exit(1)
    _exec("./upload_package.sh", bash=True)


def _drain_stdin_if_necessary() -> None:
    try:
        # if os.name == "posix":
        #     import select

        #     while True:
        #         ready, _, _ = select.select([sys.stdin], [], [], 0)
        #         if not ready:
        #             break
        #         sys.stdin.read(1)
        if os.name == "nt":
            import msvcrt

            while msvcrt.kbhit():  # type: ignore
                msvcrt.getwch()  # type: ignore
    except EOFError:
        pass
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Error draining stdin: {e}")


def _in_process_ai_commit_or_prompt_for_commit_message(
    auto_accept_aicommits: bool,
) -> None:
    cmd = "aicommits"
    if which(cmd):
        _drain_stdin_if_necessary()

        if auto_accept_aicommits:
            if os.name == "posix":
                _ = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=False,
                )
                # import pty

                # master_fd, slave_fd = pty.openpty()  # type: ignore
                # process = subprocess.Popen(
                #     cmd,
                #     shell=True,
                #     stdin=slave_fd,
                #     stdout=slave_fd,
                #     stderr=slave_fd,
                #     close_fds=True,
                # )
                # os.close(slave_fd)
                # with os.fdopen(master_fd, "rb+", buffering=0) as master:
                #     for line in master:
                #         line_str = line.decode("utf-8", errors="ignore").strip()
                #         print(line_str)
                #         if "Yes" in line_str and "No" in line_str:
                #             master.write(b"\n")
                #     process.wait()

            elif os.name == "nt":
                from winpty import PtyProcess

                proc = PtyProcess.spawn(cmd)
                while proc.isalive():
                    line = proc.readline()

                    linestr: str
                    if isinstance(line, bytes):
                        linestr = line.decode("utf-8", errors="ignore")
                    else:
                        linestr = line
                    linestr = linestr.strip()
                    if not line:
                        break
                    print(linestr)
                    if "quota" in linestr.lower():
                        print("Quota exceeded.")
                        proc.terminate()
                        raise RuntimeError("Quota exceeded.")
                    if "Yes" in linestr and "No" in linestr:
                        proc.write("\r\n")  # simulate ENTER
                    time.sleep(0.1)
                proc.wait()
                rtn = proc.exitstatus
                if rtn != 0:
                    print(f"Error: {cmd} returned {rtn}")
                    raise SystemExit(rtn)
        else:
            subprocess.run(cmd, shell=True)
    else:
        # Manual commit
        msg = input("Commit message: ")
        msg = f'"{msg}"'
        _exec(f"git commit -m {msg}", bash=False)


def _ai_commit_or_prompt_for_commit_message(no_autoaccept: bool) -> None:
    from multiprocessing import Process

    proc = Process(
        target=_in_process_ai_commit_or_prompt_for_commit_message,
        args=(not no_autoaccept,),  # Auto-accept unless no_autoaccept is True
    )
    proc.start()
    proc.join()
    rtn = proc.exitcode
    if rtn != 0:
        print(f"Error: aicommit2 returned {rtn}")
        commit_message = input(
            "AI Commit failed! (Check your billing balance for OpenAI)\nManually enter commit message: "
        )
        commit_message = f'"{commit_message}"'
        _exec(f"git commit -m {commit_message}", bash=False)


# demo help message


def main() -> int:
    """Run git status, lint, test, add, and commit."""

    args = _parse_args()
    verbose = args.verbose

    git_path = check_environment()
    os.chdir(str(git_path))
    try:
        repo = Repo(".")
        git_status_str = repo.git.status()
        print(git_status_str)
        has_untracked = len(repo.untracked_files) > 0
        if has_untracked:
            print("There are untracked files.")
            answer_yes = get_answer_yes_or_no("Continue?", "y")
            if not answer_yes:
                print("Aborting.")
                return 1
            for untracked_file in repo.untracked_files:
                answer_yes = get_answer_yes_or_no(f"  Add {untracked_file}?", "y")
                if answer_yes:
                    _exec(f"git add {untracked_file}", bash=False)
                else:
                    print(f"  Skipping {untracked_file}")
        if os.path.exists("./lint") and not args.no_lint:
            cmd = "./lint" + (" --verbose" if verbose else "")
            # rtn = _exec(cmd, bash=True, die=True)  # Come back to this

            cmd = _to_exec_str(cmd, bash=True)
            uv_resolved_dependencies = True
            proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            with proc:
                assert proc.stdout is not None
                for line in proc.stdout:
                    linestr = line.decode("utf-8", errors="ignore").strip()
                    print(linestr)
                    if "No solution found when resolving dependencies" in linestr:
                        uv_resolved_dependencies = False
            proc.wait()
            if proc.returncode != 0:
                print("Error: Linting failed.")
                if uv_resolved_dependencies:
                    sys.exit(1)
                answer_yes = get_answer_yes_or_no(
                    "'uv pip install -e . --refresh'?", "n"
                )
                if not answer_yes:
                    print("Aborting.")
                    sys.exit(1)
                for _ in range(3):
                    refresh_rtn = _exec(
                        "uv pip install -e . --refresh", bash=True, die=False
                    )
                    if refresh_rtn == 0:
                        break
                else:
                    print("Error: uv pip install -e . --refresh failed.")
                    sys.exit(1)
        if not args.no_test and os.path.exists("./test"):
            _exec("./test" + (" --verbose" if verbose else ""), bash=True)
        _exec("git add .", bash=False)
        _ai_commit_or_prompt_for_commit_message(args.no_autoaccept)
        if not args.no_push:
            _exec("git push", bash=False)
        if args.publish:
            _publish()
    except KeyboardInterrupt:
        print("Aborting")
        return 1
    return 0


if __name__ == "__main__":
    main()
