"""Tests for ayushman.registry"""

import json

import pytest

import ayushman.registry as registry
from ayushman.result import InstallResult


def make_install_result(**overrides) -> InstallResult:
    defaults = dict(
        package_name="pdf-toolkit",
        version="1.0.0",
        zip_file_name="pdf-toolkit.zip",
        install_path=r"C:\bin\pdf-toolkit\1.0.0",
        success=True,
        error_message=None,
        metadata={"author": "someone"},
        metadata_path=r"C:\bin\pdf-toolkit\1.0.0\metadata.json",
    )
    defaults.update(overrides)
    return InstallResult(**defaults)


@pytest.fixture
def isolated_registry(tmp_path, monkeypatch):
    """
    registry.REGISTRY_PATH is bound to global_paths.GLOBAL_METADATA at
    import time (a plain attribute assignment, not a re-lookup on every
    call), so patching global_paths.GLOBAL_METADATA after the fact has no
    effect here. We patch registry.REGISTRY_PATH itself instead.
    """
    fake_path = tmp_path / "metadata.json"
    monkeypatch.setattr(registry, "REGISTRY_PATH", fake_path)
    return fake_path


class TestEnsureAndReadMetadata:
    def test_creates_file_with_empty_list_if_missing(self, isolated_registry):
        assert not isolated_registry.exists()
        data = registry._read_metadata()
        assert isolated_registry.exists()
        assert data == {"installed_packages": []}

    def test_creates_parent_directories_if_missing(self, tmp_path, monkeypatch):
        nested_path = tmp_path / "nested" / "dir" / "metadata.json"
        monkeypatch.setattr(registry, "REGISTRY_PATH", nested_path)
        registry._read_metadata()
        assert nested_path.exists()

    def test_does_not_overwrite_existing_file(self, isolated_registry):
        isolated_registry.write_text(
            json.dumps({"installed_packages": [{"name": "x", "version": "1"}]})
        )
        data = registry._read_metadata()
        assert data == {"installed_packages": [{"name": "x", "version": "1"}]}


class TestAddPackage:
    def test_adds_new_package_entry(self, isolated_registry):
        registry.add_package(make_install_result())
        data = json.loads(isolated_registry.read_text())
        assert len(data["installed_packages"]) == 1
        entry = data["installed_packages"][0]
        assert entry["name"] == "pdf-toolkit"
        assert entry["version"] == "1.0.0"
        assert entry["install_path"] == r"C:\bin\pdf-toolkit\1.0.0"

    def test_replaces_existing_entry_for_same_name_and_version(self, isolated_registry):
        registry.add_package(make_install_result(install_path="old-path"))
        registry.add_package(make_install_result(install_path="new-path"))

        data = json.loads(isolated_registry.read_text())
        matching = [p for p in data["installed_packages"] if p["name"] == "pdf-toolkit"]
        assert len(matching) == 1
        assert matching[0]["install_path"] == "new-path"

    def test_keeps_separate_entries_for_different_versions(self, isolated_registry):
        registry.add_package(make_install_result(version="1.0.0"))
        registry.add_package(make_install_result(version="2.0.0"))

        data = json.loads(isolated_registry.read_text())
        versions = sorted(p["version"] for p in data["installed_packages"])
        assert versions == ["1.0.0", "2.0.0"]

    def test_keeps_separate_entries_for_different_packages(self, isolated_registry):
        registry.add_package(make_install_result(package_name="pdf-toolkit"))
        registry.add_package(make_install_result(package_name="cpp-cloc"))

        data = json.loads(isolated_registry.read_text())
        names = sorted(p["name"] for p in data["installed_packages"])
        assert names == ["cpp-cloc", "pdf-toolkit"]


class TestListPackage:
    def test_empty_when_nothing_installed(self, isolated_registry):
        assert registry.list_package() == []

    def test_formats_as_name_space_version(self, isolated_registry):
        registry.add_package(
            make_install_result(package_name="pdf-toolkit", version="1.0.0")
        )
        assert registry.list_package() == ["pdf-toolkit 1.0.0"]


class TestGetInstalledVersion:
    def test_returns_none_if_not_installed(self, isolated_registry):
        assert registry.get_installed_version("pdf-toolkit") is None

    def test_returns_version_if_installed(self, isolated_registry):
        registry.add_package(
            make_install_result(package_name="pdf-toolkit", version="1.2.3")
        )
        assert registry.get_installed_version("pdf-toolkit") == "1.2.3"


class TestIsPackageInstalled:
    def test_false_if_not_installed(self, isolated_registry):
        assert registry.is_package_installed("pdf-toolkit") is False

    def test_true_if_installed(self, isolated_registry):
        registry.add_package(make_install_result(package_name="pdf-toolkit"))
        assert registry.is_package_installed("pdf-toolkit") is True


class TestGetPackageMetadata:
    def test_empty_dict_if_not_found(self, isolated_registry):
        assert registry.get_package_metadata("pdf-toolkit") == {}

    def test_returns_entry_if_found(self, isolated_registry):
        registry.add_package(
            make_install_result(package_name="pdf-toolkit", version="1.0.0")
        )
        meta = registry.get_package_metadata("pdf-toolkit")
        assert meta["name"] == "pdf-toolkit"
        assert meta["version"] == "1.0.0"


class TestRemovePackage:
    def test_returns_false_if_not_found(self, isolated_registry):
        assert registry.remove_package("pdf-toolkit") is False

    def test_removes_existing_package_and_returns_true(self, isolated_registry):
        registry.add_package(make_install_result(package_name="pdf-toolkit"))
        removed = registry.remove_package("pdf-toolkit")
        assert removed is True
        assert registry.is_package_installed("pdf-toolkit") is False

    def test_removing_one_package_does_not_affect_others(self, isolated_registry):
        registry.add_package(make_install_result(package_name="pdf-toolkit"))
        registry.add_package(make_install_result(package_name="cpp-cloc"))

        registry.remove_package("pdf-toolkit")

        assert registry.is_package_installed("pdf-toolkit") is False
        assert registry.is_package_installed("cpp-cloc") is True


class TestBinInPathFlag:
    def test_defaults_to_false(self, isolated_registry):
        assert registry.get_bin_in_path() is False

    def test_set_true_then_read_back(self, isolated_registry):
        registry.set_bin_in_path(True)
        assert registry.get_bin_in_path() is True

    def test_set_false_then_read_back(self, isolated_registry):
        registry.set_bin_in_path(True)
        registry.set_bin_in_path(False)
        assert registry.get_bin_in_path() is False

    def test_flag_persists_alongside_installed_packages(self, isolated_registry):
        registry.add_package(make_install_result())
        registry.set_bin_in_path(True)

        assert registry.get_bin_in_path() is True
        assert registry.is_package_installed("pdf-toolkit") is True
