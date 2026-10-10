import os
import stat
import sys
import tempfile
import unittest

from zcmds.cmds.common.losslesscut import find_system_losslesscut


def _make_exe(d: str) -> str:
    p = os.path.join(d, "losslesscut")
    with open(p, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\n")
    os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
    return p


@unittest.skipIf(sys.platform == "win32", "POSIX PATH lookup only")
class LosslessCutLookupTest(unittest.TestCase):
    def test_skips_self_and_finds_real(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            shim = _make_exe(a)
            real = _make_exe(b)
            path = os.pathsep.join([a, b])
            self.assertEqual(find_system_losslesscut(path, shim), real)

    def test_none_when_only_self(self) -> None:
        with tempfile.TemporaryDirectory() as a:
            shim = _make_exe(a)
            self.assertIsNone(find_system_losslesscut(a, shim))


if __name__ == "__main__":
    unittest.main()
