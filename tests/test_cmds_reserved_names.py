import sys
import unittest
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

CMDS_TXT = Path(__file__).resolve().parent.parent / "src" / "zcmds" / "cmds.txt"

# POSIX / coreutils utilities that programs exec by name. zcmds is a universal
# wheel whose entry points install on every platform, so it must never register
# one of these (see issue #17: `test` shadowing broke nixos-rebuild).
RESERVED_NAMES = {
    "[",
    "basename",
    "cat",
    "chmod",
    "cp",
    "cut",
    "date",
    "dirname",
    "echo",
    "env",
    "false",
    "find",
    "grep",
    "head",
    "id",
    "ln",
    "ls",
    "mkdir",
    "mv",
    "printenv",
    "printf",
    "pwd",
    "readlink",
    "realpath",
    "rm",
    "sed",
    "sh",
    "sort",
    "tail",
    "tee",
    "test",
    "touch",
    "tr",
    "true",
    "uname",
    "uniq",
    "wc",
    "which",
    "xargs",
    "yes",
}


def registered_command_names() -> set[str]:
    """Return the console script names declared in cmds.txt."""
    names = set()
    for line in CMDS_TXT.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            names.add(line.split("=", 1)[0].strip())
    return names


class TestReservedCommandNames(unittest.TestCase):
    def test_no_posix_utility_names(self) -> None:
        """cmds.txt must not shadow POSIX/coreutils utilities."""
        collisions = sorted(registered_command_names() & RESERVED_NAMES)
        self.assertEqual(collisions, [], f"cmds.txt shadows POSIX utilities: {collisions}")

    @unittest.skipIf(sys.platform != "win32", "zcmds_win32 is only installed on Windows")
    def test_no_overlap_with_zcmds_win32(self) -> None:
        """zcmds and zcmds_win32 must not install the same console script."""
        try:
            win32_dist = distribution("zcmds_win32")
        except PackageNotFoundError:
            self.skipTest("zcmds_win32 is not installed")
        win32_names = {
            ep.name for ep in win32_dist.entry_points if ep.group == "console_scripts"
        }
        overlap = sorted(registered_command_names() & win32_names)
        self.assertEqual(overlap, [], f"console scripts in both packages: {overlap}")


if __name__ == "__main__":
    unittest.main()
