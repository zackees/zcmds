# Open Issue Strategies

Last researched: 2026-06-02

This file tracks the current strategy for each open GitHub issue in `zackees/zcmds`.
Open issues researched: #4, #5, #7, #8, #10.

## Build Badges

The badge-backed workflows were updated before this issue review:

- README badges now explicitly target the `master` branch.
- All workflows now support `workflow_dispatch` so stale failing runs can be refreshed without a no-op push.
- Lint no longer installs the missing `requirements.testing.txt`; it runs the repo's current `uv` test group directly.
- Linux and macOS tests now run the checked-in unittest command through `uv`, with headless audio settings for the real `beep()` test.
- Windows tests keep the pip install path because the current Windows dependency stack passes there and `uv` can reject reserved script names from `zcmds_win32`.

## #4 - `pipx install zcmds isn't working`

Issue: Debian 12 rejects a system `pip install zcmds` because of PEP 668's externally managed environment rules.

Evidence:

- `README.md` still leads with `pip install zcmds`.
- `pyproject.toml` already depends on `pipx`, and release notes mention `pipx` for related tooling, but install docs do not make `pipx` the primary app install path.

Strategy:

- Update the user-facing install docs to recommend `pipx install zcmds` for normal CLI installation.
- Keep `python -m venv ... && pip install zcmds` as the fallback path for systems without `pipx`.
- Keep `pip install -e .` or `uv run pip install -e .` only under development installation docs.
- Add a packaging smoke check that builds a wheel and verifies `zcmds` starts from an isolated environment. A full `pipx install .` smoke test is useful if CI time stays reasonable.

Likely resolution: documentation plus packaging smoke coverage. No source change appears necessary.

## #5 - `askai - Entering 'Exit' creates a loop`

Issue: Entering `Exit` in `askai` reportedly caused an infinite loop.

Evidence:

- `askai` is no longer implemented in this repository; `src/zcmds/get_cmds.py` exposes it as an external command.
- `pyproject.toml` depends on `advanced-askai`, and `uv.lock` currently resolves `advanced-askai==1.0.2`.
- README release notes say `askai` was moved into its own package and later improved around `exit` handling.

Strategy:

- Reproduce against the currently resolved `advanced-askai` version, not against this repository's source tree.
- If the bug is fixed upstream, pin a minimum `advanced-askai` version in `pyproject.toml` and close the issue with the verified version.
- If the bug still reproduces, fix it in `advanced-askai`, release that package, then update this repo's dependency lower bound and lockfile.
- Add a small console-input regression test in the external `advanced-askai` package for `exit`, `Exit`, and EOF behavior.

Likely resolution: upstream package fix or minimum-version bump in this repo.

## #7 - `ModuleNotFoundError: imgai`

Issue: `imgai` failed with `ModuleNotFoundError: No module named 'zcmds.cmds.common.inputimeout'`.

Evidence:

- Current `src/zcmds/cmds/common/imgai.py` imports `inputimeout` from the installed package, not from a missing local module.
- `pyproject.toml` declares `inputimeout` as a runtime dependency.
- The command is still registered in `src/zcmds/cmds.txt`.
- Maintainer discussion says the tool is old and may be removed.

Strategy:

- First verify the installed console entry point with `imgai --help` or an import-only smoke test. If the issue no longer reproduces, close it as already fixed.
- Decide whether `imgai` should remain supported. If not, remove it from `src/zcmds/cmds.txt` and README command docs in one explicit deprecation/removal change.
- If keeping it, add an import smoke test and modernize the command around the current image-generation API before advertising it as working.

Likely resolution: close as already fixed for the import bug, then separately decide whether to remove or modernize the old command.

## #8 - `transcribe-anything torch version error`

Issue: Installing/using `transcribe-anything` failed on Python 3.12 because an older dependency path wanted `torch==2.1.2`, while the reporter's environment only exposed newer torch builds.

Evidence:

- `pyproject.toml` requires `transcribe-anything>=2.7.27`.
- `uv.lock` currently resolves `transcribe-anything==3.0.11`.
- The issue is about the external transcribe stack rather than local zcmds command code.
- The project currently advertises `requires-python = ">=3.10"` without a narrower upper bound or Python-version-specific guidance.

Strategy:

- Reproduce install and `transcribe-anything --help` under Python 3.12 using the current lock/dependency set.
- If current `transcribe-anything` resolves the torch conflict, close the issue with the tested Python and package versions.
- If Python 3.12 remains unreliable, either cap supported Python versions in docs/metadata or move `transcribe-anything` behind an optional extra so the core zcmds install is not blocked by a heavyweight ML stack.
- Add a Python 3.12 packaging smoke job only after the dependency path is known to be stable enough for CI.

Likely resolution: verify current external dependency behavior, then either close with version evidence or isolate the transcribe dependency.

## #10 - `Unrecognized option 'cq'`

Issue: `vid2mp4 --rencode --nvenc --crf 23 ...` emitted `-cq 23`, and ffmpeg rejected it with `Unrecognized option 'cq'`.

Evidence:

- Current `src/zcmds/cmds/common/vid2mp4.py` still maps NVENC quality to `-cq`.
- Issue comments propose using NVENC constant-QP arguments: `-rc constqp -qp 23`.
- The command currently uses `os.system` and prints `Generated ...` regardless of ffmpeg's exit status.

Strategy:

- Replace the NVENC quality mapping with ffmpeg-compatible arguments, likely `-rc constqp -qp <value>` for the current `--crf` compatibility flag.
- Build the ffmpeg command through a helper function so unit tests can assert x264 and NVENC command arguments without requiring a GPU.
- Replace `os.system` with `subprocess.run` and return ffmpeg's exit code so failures are visible.
- Add a regression test using the issue's command shape and a small local fixture or command-builder test.

Likely resolution: source fix plus command-generation tests. This is the most direct open product bug.
