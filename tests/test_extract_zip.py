"""Tests for ayushman.extract_zip.extract_zip_file"""

import json
import zipfile
from pathlib import Path

import pytest

import ayushman.extract_zip as extract_zip
from ayushman.result import InstallResult

# ---------- Helpers ----------


def make_install_result(**overrides) -> InstallResult:
    defaults = dict(
        package_name="pdf-toolkit",
        version="1.0.0",
        zip_file_name="",  # set per-test
        install_path="",
        success=False,
        error_message=None,
        metadata={"author": "JourneyCodesAyush", "license": "MIT"},
        metadata_path="",
    )
    defaults.update(overrides)
    return InstallResult(**defaults)


def make_zip(path: Path, entries: dict) -> Path:
    """entries: mapping of in-zip filename -> file content bytes."""
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return path


# ---------- Fixture: isolate global_paths ----------


@pytest.fixture
def isolated_paths(tmp_path, monkeypatch):
    package_dir = tmp_path / "packages"
    bin_dir = tmp_path / "bin"
    monkeypatch.setattr(extract_zip.global_paths, "PACKAGE_DIR", package_dir)
    monkeypatch.setattr(extract_zip.global_paths, "BIN_DIR", bin_dir)
    return package_dir, bin_dir


# ---------- Happy path ----------


class TestHappyPath:
    def test_single_exe_extracted_and_linked(self, tmp_path, isolated_paths):
        package_dir, bin_dir = isolated_paths
        zip_path = make_zip(tmp_path / "pkg.zip", {"pdf-toolkit.exe": b"fake binary"})

        install_result = make_install_result(zip_file_name=str(zip_path))
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is True
        assert result.error_message is None

        extracted = package_dir / "pdf-toolkit" / "1.0.0" / "pdf-toolkit.exe"
        assert extracted.exists()
        assert extracted.read_bytes() == b"fake binary"

        hardlink = bin_dir / "pdf-toolkit.exe"
        assert hardlink.exists()
        assert hardlink.read_bytes() == b"fake binary"

        assert result.install_path == str(package_dir / "pdf-toolkit" / "1.0.0")

    def test_metadata_json_written_correctly(self, tmp_path, isolated_paths):
        package_dir, _ = isolated_paths
        zip_path = make_zip(tmp_path / "pkg.zip", {"tool.exe": b"data"})
        metadata = {"author": "someone", "license": "MIT", "version": "1.0.0"}

        install_result = make_install_result(
            zip_file_name=str(zip_path), metadata=metadata
        )
        result = extract_zip.extract_zip_file(install_result)

        metadata_path = Path(result.metadata_path)
        assert metadata_path.exists()
        assert json.loads(metadata_path.read_text()) == metadata

    def test_directories_created_if_missing(self, tmp_path, isolated_paths):
        package_dir, bin_dir = isolated_paths
        assert not package_dir.exists()
        assert not bin_dir.exists()

        zip_path = make_zip(tmp_path / "pkg.zip", {"tool.exe": b"data"})
        install_result = make_install_result(zip_file_name=str(zip_path))
        extract_zip.extract_zip_file(install_result)

        assert package_dir.exists()
        assert bin_dir.exists()


# ---------- Filtering behavior ----------


class TestFileFiltering:
    def test_non_exe_files_ignored(self, tmp_path, isolated_paths):
        package_dir, bin_dir = isolated_paths
        zip_path = make_zip(
            tmp_path / "pkg.zip",
            {
                "tool.exe": b"binary",
                "README.txt": b"read me",
                "tool.dll": b"dll data",
            },
        )
        install_result = make_install_result(zip_file_name=str(zip_path))
        result = extract_zip.extract_zip_file(install_result)

        pkg_folder = package_dir / "pdf-toolkit" / "1.0.0"
        assert (pkg_folder / "tool.exe").exists()
        assert not (pkg_folder / "README.txt").exists()
        assert not (pkg_folder / "tool.dll").exists()
        assert result.success is True

    def test_case_insensitive_exe_extension(self, tmp_path, isolated_paths):
        package_dir, bin_dir = isolated_paths
        zip_path = make_zip(tmp_path / "pkg.zip", {"TOOL.EXE": b"binary"})
        install_result = make_install_result(zip_file_name=str(zip_path))
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is True
        assert (bin_dir / "pdf-toolkit.exe").exists()

    def test_nested_zip_paths_are_flattened(self, tmp_path, isolated_paths):
        package_dir, bin_dir = isolated_paths
        zip_path = make_zip(tmp_path / "pkg.zip", {"subdir/nested/tool.exe": b"binary"})
        install_result = make_install_result(zip_file_name=str(zip_path))
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is True
        pkg_folder = package_dir / "pdf-toolkit" / "1.0.0"
        # Extracted flat -- no subdir/nested structure preserved
        assert (pkg_folder / "tool.exe").exists()
        assert not (pkg_folder / "subdir").exists()

    def test_directory_entries_in_zip_do_not_error(self, tmp_path, isolated_paths):
        zip_path = tmp_path / "pkg.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("emptydir/", "")  # directory entry
            zf.writestr("tool.exe", b"binary")

        install_result = make_install_result(zip_file_name=str(zip_path))
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is True


# ---------- Upgrade / hardlink replacement ----------


class TestUpgradeBehavior:
    def test_existing_hardlink_is_replaced(self, tmp_path, isolated_paths):
        package_dir, bin_dir = isolated_paths
        bin_dir.mkdir(parents=True)
        old_link = bin_dir / "pdf-toolkit.exe"
        old_link.write_bytes(b"old version")

        zip_path = make_zip(tmp_path / "pkg.zip", {"pdf-toolkit.exe": b"new version"})
        install_result = make_install_result(
            zip_file_name=str(zip_path), version="2.0.0"
        )
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is True
        assert old_link.read_bytes() == b"new version"

    def test_multiple_exes_in_zip_last_one_wins_hardlink(
        self, tmp_path, isolated_paths
    ):
        """
        Documents current behavior: if a package zip contains more than one
        .exe, every .exe gets extracted into the versioned package folder,
        but only the last one processed (order from zip.infolist(), which
        is not guaranteed) ends up hard-linked into bin/. This may be worth
        revisiting -- flagging via this test rather than silently asserting
        it's correct.
        """
        package_dir, bin_dir = isolated_paths
        zip_path = make_zip(
            tmp_path / "pkg.zip",
            {"tool_a.exe": b"binary a", "tool_b.exe": b"binary b"},
        )
        install_result = make_install_result(zip_file_name=str(zip_path))
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is True
        pkg_folder = package_dir / "pdf-toolkit" / "1.0.0"
        # Both extracted...
        assert (pkg_folder / "tool_a.exe").exists()
        assert (pkg_folder / "tool_b.exe").exists()
        # ...but only one is linked, and it's whichever zip.infolist() gave last
        hardlink = bin_dir / "pdf-toolkit.exe"
        assert hardlink.exists()
        assert hardlink.read_bytes() == b"binary b"


# ---------- Failure modes ----------


class TestFailureModes:
    def test_invalid_zip_file_sets_failure(self, tmp_path, isolated_paths):
        bad_zip = tmp_path / "not_a_zip.zip"
        bad_zip.write_bytes(b"this is not a zip file")

        install_result = make_install_result(zip_file_name=str(bad_zip))
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is False
        assert result.error_message is not None

    def test_missing_zip_file_sets_failure(self, tmp_path, isolated_paths):
        missing_zip = tmp_path / "does_not_exist.zip"

        install_result = make_install_result(zip_file_name=str(missing_zip))
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is False
        assert result.error_message is not None

    def test_failure_does_not_set_install_path_or_metadata_path(
        self, tmp_path, isolated_paths
    ):
        bad_zip = tmp_path / "bad.zip"
        bad_zip.write_bytes(b"garbage")

        install_result = make_install_result(
            zip_file_name=str(bad_zip),
            install_path="unchanged",
            metadata_path="unchanged",
        )
        result = extract_zip.extract_zip_file(install_result)

        assert result.success is False
        # Function returns early on exception, before these get overwritten
        assert result.install_path == "unchanged"
        assert result.metadata_path == "unchanged"
