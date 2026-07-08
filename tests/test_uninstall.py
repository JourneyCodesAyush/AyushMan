"""Tests for ayushman.uninstall.uninstall_package"""

import pytest

import ayushman.uninstall as uninstall


@pytest.fixture
def isolated_paths(tmp_path, monkeypatch):
    package_dir = tmp_path / "packages"
    bin_dir = tmp_path / "bin"
    package_dir.mkdir()
    bin_dir.mkdir()
    monkeypatch.setattr(uninstall.global_paths, "PACKAGE_DIR", package_dir)
    monkeypatch.setattr(uninstall.global_paths, "BIN_DIR", bin_dir)
    return package_dir, bin_dir


def make_installed_package(package_dir, bin_dir, package_name, versions):
    """Set up an on-disk installed package with one or more versions."""
    pkg_folder = package_dir / package_name
    pkg_folder.mkdir(parents=True, exist_ok=True)
    for version in versions:
        version_folder = pkg_folder / version
        version_folder.mkdir()
        exe_path = version_folder / f"{package_name}.exe"
        exe_path.write_bytes(b"fake binary")
    # Only the "active" bin link needs to exist for realistic behavior.
    (bin_dir / f"{package_name}.exe").write_bytes(b"fake binary")
    return pkg_folder


class TestUninstallNonexistentPackage:
    def test_returns_failure_result(self, isolated_paths):
        package_dir, bin_dir = isolated_paths
        result = uninstall.uninstall_package("does-not-exist")

        assert result.success is False
        assert result.versions == []
        assert result.removed_bins == []
        assert result.removed_packages == []
        assert "does not exist" in result.error_message


class TestUninstallExistingPackage:
    def test_removes_package_folder_and_bin_link(self, isolated_paths):
        package_dir, bin_dir = isolated_paths
        make_installed_package(package_dir, bin_dir, "pdf-toolkit", ["1.0.0"])

        result = uninstall.uninstall_package("pdf-toolkit")

        assert result.success is True
        assert result.error_message == ""
        assert not (package_dir / "pdf-toolkit").exists()
        assert not (bin_dir / "pdf-toolkit.exe").exists()
        assert result.removed_packages == [str(package_dir / "pdf-toolkit")]
        assert result.removed_bins == [str(bin_dir / "pdf-toolkit.exe")]

    def test_reports_all_installed_versions(self, isolated_paths):
        package_dir, bin_dir = isolated_paths
        make_installed_package(package_dir, bin_dir, "pdf-toolkit", ["1.0.0", "2.0.0"])

        result = uninstall.uninstall_package("pdf-toolkit")

        assert sorted(result.versions) == ["1.0.0", "2.0.0"]
        assert result.success is True

    def test_does_not_fail_if_bin_link_already_missing(self, isolated_paths):
        package_dir, bin_dir = isolated_paths
        make_installed_package(package_dir, bin_dir, "pdf-toolkit", ["1.0.0"])
        (bin_dir / "pdf-toolkit.exe").unlink()

        result = uninstall.uninstall_package("pdf-toolkit")

        assert result.success is True
        assert result.removed_bins == []
        assert result.removed_packages == [str(package_dir / "pdf-toolkit")]

    def test_only_removes_bins_belonging_to_the_target_package(self, isolated_paths):
        package_dir, bin_dir = isolated_paths
        make_installed_package(package_dir, bin_dir, "pdf-toolkit", ["1.0.0"])
        make_installed_package(package_dir, bin_dir, "cpp-cloc", ["1.0.0"])

        uninstall.uninstall_package("pdf-toolkit")

        assert not (bin_dir / "pdf-toolkit.exe").exists()
        assert (bin_dir / "cpp-cloc.exe").exists()
        assert (package_dir / "cpp-cloc").exists()


class TestUninstallFailureMode:
    def test_failure_during_folder_removal_sets_error_message(
        self, isolated_paths, monkeypatch
    ):
        package_dir, bin_dir = isolated_paths
        make_installed_package(package_dir, bin_dir, "pdf-toolkit", ["1.0.0"])

        def raise_error(path):
            raise OSError("simulated deletion failure")

        monkeypatch.setattr(uninstall.shutil, "rmtree", raise_error)

        result = uninstall.uninstall_package("pdf-toolkit")

        assert result.success is False
        assert "simulated deletion failure" in result.error_message
        # Bin links are removed before the folder-removal step, so the
        # bin link cleanup should still be reflected even though the
        # overall operation ultimately failed.
        assert result.removed_bins == [str(bin_dir / "pdf-toolkit.exe")]
        assert result.removed_packages == []
