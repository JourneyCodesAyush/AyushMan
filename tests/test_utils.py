"""Tests for ayushman.utils.get_sha256"""

import hashlib

import pytest

from ayushman.utils import get_sha256


class TestGetSha256:
    def test_matches_hashlib_for_small_file(self, tmp_path):
        file_path = tmp_path / "small.bin"
        content = b"hello world"
        file_path.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()
        assert get_sha256(str(file_path)) == expected

    def test_matches_hashlib_for_file_larger_than_chunk_size(self, tmp_path):
        # get_sha256 reads in 4096-byte chunks; use a file larger than that
        # to make sure the chunked read loop covers multiple iterations.
        file_path = tmp_path / "large.bin"
        content = b"x" * 10_000 + b"y" * 5_000
        file_path.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()
        assert get_sha256(str(file_path)) == expected

    def test_empty_file_matches_hashlib_of_empty_bytes(self, tmp_path):
        file_path = tmp_path / "empty.bin"
        file_path.write_bytes(b"")

        expected = hashlib.sha256(b"").hexdigest()
        assert get_sha256(str(file_path)) == expected

    def test_different_content_produces_different_hash(self, tmp_path):
        file_a = tmp_path / "a.bin"
        file_b = tmp_path / "b.bin"
        file_a.write_bytes(b"content a")
        file_b.write_bytes(b"content b")

        assert get_sha256(str(file_a)) != get_sha256(str(file_b))

    def test_raises_for_missing_file(self, tmp_path):
        missing = tmp_path / "does_not_exist.bin"
        with pytest.raises(FileNotFoundError):
            get_sha256(str(missing))
