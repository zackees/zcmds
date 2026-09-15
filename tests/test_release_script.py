import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / ".github" / "scripts" / "release.py"

_spec = importlib.util.spec_from_file_location("auto_release_script", SCRIPT)
assert _spec is not None and _spec.loader is not None
release = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = release
_spec.loader.exec_module(release)

NEEDS_TOMLLIB = unittest.skipIf(sys.version_info < (3, 11), "tomllib needs Python 3.11+")


def reader(files: dict[str, str]):
    return files.get


class TestReadProject(unittest.TestCase):
    @NEEDS_TOMLLIB
    def test_static_version(self) -> None:
        files = {"pyproject.toml": '[project]\nname = "pkg_x"\nversion = "1.2.3"\n'}
        self.assertEqual(release.read_project(reader(files)), ("pkg_x", "1.2.3"))

    @NEEDS_TOMLLIB
    def test_attr_version_in_src_layout(self) -> None:
        files = {
            "pyproject.toml": (
                '[project]\nname = "pkg"\ndynamic = ["version"]\n'
                '[tool.setuptools.dynamic]\nversion = { attr = "pkg.__version__" }\n'
            ),
            "src/pkg/__init__.py": '__version__ = "4.5.6"\n__all__ = ["__version__"]\n',
        }
        self.assertEqual(release.read_project(reader(files)), ("pkg", "4.5.6"))

    @NEEDS_TOMLLIB
    def test_missing_version_raises(self) -> None:
        files = {"pyproject.toml": '[project]\nname = "pkg"\n'}
        with self.assertRaises(ValueError):
            release.read_project(reader(files))

    @NEEDS_TOMLLIB
    def test_reads_this_repository(self) -> None:
        name, version = release.read_project(release.working_tree_reader(REPO_ROOT))
        self.assertTrue(name)
        self.assertRegex(version, r"^\d+\.\d+\.\d+")


class TestDecide(unittest.TestCase):
    def _decide(self, **overrides):
        params = dict(
            event="push",
            ref="refs/heads/main",
            default_branch="main",
            dry_run=True,
            current_version="1.0.1",
            previous_version="1.0.0",
            published_files=set(),
        )
        params.update(overrides)
        decision = release.decide(**params)
        return decision.should_build, decision.should_publish

    def test_push_with_version_bump_publishes(self) -> None:
        self.assertEqual(self._decide(), (True, True))

    def test_push_without_version_change_skips(self) -> None:
        self.assertEqual(self._decide(previous_version="1.0.1"), (False, False))

    def test_push_of_version_already_on_pypi_skips(self) -> None:
        published = {"pkg-1.0.1-py3-none-any.whl"}
        self.assertEqual(self._decide(published_files=published), (False, False))

    def test_push_to_other_branch_skips(self) -> None:
        self.assertEqual(self._decide(ref="refs/heads/feature"), (False, False))

    def test_pull_request_builds_without_publishing(self) -> None:
        self.assertEqual(
            self._decide(event="pull_request", ref="refs/pull/1/merge"), (True, False)
        )

    def test_dispatch_dry_run_builds_without_publishing(self) -> None:
        self.assertEqual(self._decide(event="workflow_dispatch"), (True, False))

    def test_dispatch_publishes_from_default_branch(self) -> None:
        self.assertEqual(
            self._decide(event="workflow_dispatch", dry_run=False, previous_version=None),
            (True, True),
        )

    def test_dispatch_never_publishes_from_other_branch(self) -> None:
        self.assertEqual(
            self._decide(
                event="workflow_dispatch", dry_run=False, ref="refs/heads/feature"
            ),
            (True, False),
        )


def _write_wheel(path: Path, name: str, version: str, extra: tuple[str, ...] = ()) -> None:
    dist_info = f"{name}-{version}.dist-info"
    with zipfile.ZipFile(path, "w") as wheel:
        wheel.writestr(
            f"{dist_info}/METADATA",
            f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n",
        )
        wheel.writestr(f"{dist_info}/entry_points.txt", "[console_scripts]\nx = pkg:main\n")
        for member in extra:
            wheel.writestr(member, "")


class TestVerifyDist(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dist = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_valid_distributions_pass(self) -> None:
        _write_wheel(self.dist / "my_pkg-1.0.0-py3-none-any.whl", "my_pkg", "1.0.0")
        (self.dist / "my_pkg-1.0.0.tar.gz").write_bytes(b"")
        self.assertEqual(release.verify_dist(self.dist, "my-pkg", "1.0.0"), [])

    def test_dotfiles_written_by_uv_build_are_ignored(self) -> None:
        _write_wheel(self.dist / "my_pkg-1.0.0-py3-none-any.whl", "my_pkg", "1.0.0")
        (self.dist / "my_pkg-1.0.0.tar.gz").write_bytes(b"")
        (self.dist / ".gitignore").write_text("*\n")
        self.assertEqual(release.verify_dist(self.dist, "my_pkg", "1.0.0"), [])
        self.assertEqual(
            release.dist_files(self.dist),
            ["my_pkg-1.0.0-py3-none-any.whl", "my_pkg-1.0.0.tar.gz"],
        )

    def test_publish_attestations_are_not_distributions(self) -> None:
        """pypa/gh-action-pypi-publish writes attestations PyPI never lists as files."""
        (self.dist / "my_pkg-1.0.0-py3-none-any.whl").write_bytes(b"")
        (self.dist / "my_pkg-1.0.0.tar.gz").write_bytes(b"")
        (self.dist / "my_pkg-1.0.0-py3-none-any.whl.publish.attestation").write_text("{}")
        (self.dist / "my_pkg-1.0.0.tar.gz.publish.attestation").write_text("{}")
        self.assertEqual(
            release.dist_files(self.dist),
            ["my_pkg-1.0.0-py3-none-any.whl", "my_pkg-1.0.0.tar.gz"],
        )

    def test_version_mismatch_fails(self) -> None:
        _write_wheel(self.dist / "my_pkg-0.9.0-py3-none-any.whl", "my_pkg", "0.9.0")
        (self.dist / "my_pkg-0.9.0.tar.gz").write_bytes(b"")
        self.assertTrue(release.verify_dist(self.dist, "my_pkg", "1.0.0"))

    def test_native_wheel_fails(self) -> None:
        _write_wheel(
            self.dist / "my_pkg-1.0.0-py3-none-any.whl",
            "my_pkg",
            "1.0.0",
            extra=("my_pkg/_speedups.so",),
        )
        (self.dist / "my_pkg-1.0.0.tar.gz").write_bytes(b"")
        errors = release.verify_dist(self.dist, "my_pkg", "1.0.0")
        self.assertTrue(any("native" in error for error in errors))


class TestWaitPypi(unittest.TestCase):
    def test_returns_true_once_all_files_are_visible(self) -> None:
        responses = iter([{"a.whl"}, {"a.whl", "a.tar.gz"}])
        ok = release.wait_pypi(
            "pkg",
            "1.0.0",
            {"a.whl", "a.tar.gz"},
            timeout_s=5,
            interval_s=0,
            fetch=lambda _p, _v: next(responses),
        )
        self.assertTrue(ok)

    def test_returns_false_on_timeout(self) -> None:
        ok = release.wait_pypi(
            "pkg",
            "1.0.0",
            {"a.whl"},
            timeout_s=0,
            interval_s=0,
            fetch=lambda _p, _v: set(),
        )
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
