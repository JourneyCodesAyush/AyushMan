"""Tests for ayushman.validator.validate_package"""

import pytest

from ayushman.registry_supported import SUPPORTED_PACKAGES
from ayushman.validator import validate_package


class TestValidatePackage:
    @pytest.mark.parametrize("package", list(SUPPORTED_PACKAGES.keys()))
    def test_supported_packages_return_true(self, package):
        assert validate_package(package) is True

    @pytest.mark.parametrize(
        "package",
        [
            "not-a-real-package",
            "npm",
            "pip",
            "occ2",
            "sweeps",
        ],
    )
    def test_unsupported_packages_return_false(self, package):
        assert validate_package(package) is False

    def test_empty_string_returns_false(self):
        assert validate_package("") is False

    @pytest.mark.parametrize(
        "package",
        [
            "PDF-TOOLKIT",
            "Pdf-Toolkit",
            "OCC",
        ],
    )
    def test_case_sensitivity(self, package):
        # Documents current behavior: validation is case-sensitive.
        assert validate_package(package) is False

    @pytest.mark.parametrize(
        "package",
        [
            " pdf-toolkit",
            "pdf-toolkit ",
            " pdf-toolkit ",
        ],
    )
    def test_whitespace_is_not_stripped(self, package):
        # Documents current behavior: no whitespace trimming happens.
        assert validate_package(package) is False


class TestSupportedPackagesRegistry:
    def test_registry_is_nonempty(self):
        assert len(SUPPORTED_PACKAGES) > 0

    def test_every_entry_has_a_description(self):
        for name, meta in SUPPORTED_PACKAGES.items():
            assert "description" in meta, f"{name} is missing a description"
            assert isinstance(meta["description"], str)
            assert meta["description"].strip() != ""

    def test_all_all_readme_advertised_packages_are_present(self):
        for pkg in [
            "occ",
            "sweep",
            "c-utils",
            "cpp-cloc",
            "passman",
            "mklicense",
            "pdf-toolkit",
        ]:
            assert pkg in SUPPORTED_PACKAGES
