# Changelog

## [0.1.0] - 2026-09-20

### Added

- `install`, `uninstall`, `upgrade`, `list`, `available`, `info`, and `purge` commands
- `purge` supports `--force` and `--dry-run` flags
- `-v` / `--version` flags
- ANSI color output for better terminal experience
- Hard-link based versioned installs — upgrade-safe by design
- SHA-256 verification of downloaded ZIPs before extraction
- Automatic PATH injection on first install, with cleanup on `purge`
- `available` command backed by a curated package registry
- Fork-friendly constants in `constants.py` and `registry_supported.py`
- Supported packages: `occ`, `sweep`, `c-utils`, `cpp-cloc`, `passman`, `mklicense`, `pdf-toolkit`, `lsz`
- Full test suite covering install, uninstall, registry, validation, and hashing
- CI workflow for linting and tests
- PyInstaller spec for building self-contained `ayushman.exe`

### Changed

- Renamed project from `ayuman` to `ayushman`
- Migrated to `uv` and `hatchling` build backend, dropping `requirements.txt`
- Replaced `black` + `isort` with `ruff` for formatting
- Moved to `src/ayushman/` layout
- Switched to absolute package imports throughout

### Fixed

- Packaged binary no longer crashes on unhandled exceptions — caught inside `main()`
- Non-Windows platforms are guarded at the CLI entry point
- Mutable default argument bug in `result` module
