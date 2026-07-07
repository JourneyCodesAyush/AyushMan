# AyushMan

![Python Version](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**AyushMan** is a minimal, Windows-only binary installer for ZIP-based GitHub releases from [author](https://github.com/JourneyCodesAyush)’s repositories.

> Installs prebuilt, versioned Windows binaries from the [author](https://github.com/JourneyCodesAyush)’s GitHub releases, safely and with minimal fuss.

It installs prebuilt executables directly from GitHub and keeps them isolated,
versioned, and upgrade-safe.

**AyushMan is designed to be fork-friendly.**
Project-specific configuration such as the GitHub release owner and installation layout can be customized from `src/ayushman/constants.py`.

See [Forking & Configuration](#forking--configuration) for details.

> [!WARNING]
> `AyushMan` is **NOT** a general-purpose package manager.

---

## Requirements

- Windows 10 / 11 (x86_64)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

---

## Quick Start

```powershell
git clone https://github.com/JourneyCodesAyush/ayushman.git
cd ayushman

uv venv .venv --clear

.\.venv\Scripts\Activate.ps1
# For CMD, use: .venv\Scripts\activate.bat

uv sync

# Necessary to use ayushman as a standalone command
uv pip install -e . --link-mode=copy

# Install a package
ayushman install pdf-toolkit
pdf-toolkit --help
```

> Works on Windows 10+ (x86_64). All installed executables live in `%LOCALAPPDATA%\.ayushman\bin`.

---

## Features

- Windows-only (Windows 10+, x86_64)
- Installs **prebuilt executables** from GitHub release ZIPs
- Extracts **only `.exe` files**
- Uses **hard links** for upgrade-safe installs
- Keeps packages versioned and isolated
- Supports `install`, `list`, `upgrade`, `uninstall`, `info`, and `purge` commands
- Minimal global state with JSON metadata
- No build steps, scripts, or installers

---

## Supported platforms

- Windows 10 / 11 (x86_64)
- Windows-only by design

---

## Installation

To install and run `ayushman` locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/JourneyCodesAyush/ayushman.git
   cd ayushman
   ```

2. (Recommended) Create and activate a virtual environment:

   ```ps1
   uv venv .venv --clear

   # On Windows CMD:
   .venv\Scripts\activate.bat

   # On Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   uv sync
   ```

---

## Development / Editable Install

To install `ayushman` as a local command for development:

```powershell
uv venv .venv --clear
.\.venv\Scripts\Activate.ps1  # PowerShell

uv sync
uv pip install -e . --link-mode=copy

ayushman list
```

Notes:

- Editable mode (`-e`) makes your source code changes immediately available without reinstalling.
- Make sure the virtual environment is activated; otherwise, `ayushman` won’t be on PATH.
- After the first install, `%LOCALAPPDATA%\.ayushman\bin` is automatically added to the **user PATH** so all installed binaries work in new terminals.

---

## Forking & Configuration

AyushMan keeps project-specific configuration in
`src/ayushman/constants.py`.

Forks can customize:

- `GITHUB_OWNER` - GitHub account or organization used to fetch releases
- `INSTALL_DIR_NAME` - local application directory name
- `PACKAGE_DIR_NAME` - package storage directory name
- `BIN_DIR_NAME` - executable directory name
- `METADATA_FILE_NAME` - metadata file name

Changing these values allows a fork to use its own GitHub release repositories and installation layout without modifying AyushMan's core logic.

---

## Usage

See all available commands using `-h` or `--help` flags:

<p align="center">
  <img src="assets/list-example.png" alt="AyushMan list output" width="800"/>
  <br>
</p>

Example output of `ayushman list`

Commands

```bash
ayushman install pdf-toolkit
ayushman list
ayushman available
ayushman upgrade pdf-toolkit
ayushman uninstall pdf-toolkit
```

> [!TIP]
> Use `available` to see all packages currently supported by AyushMan.

## Available Packages

AyushMan provides a curated list of packages that can be installed directly.
This avoids the need to browse GitHub manually.

```bash
ayushman available
```

```txt
Available packages:

  cpp-cloc       - Count lines of code for various languages
  c-utils        - Linux utility commands rewritten for educational purposes
  pdf-toolkit    - PDF manipulation utilities
```

---

## Installation directory layout

All ayushman data is stored in `%LOCALAPPDATA%\.ayushman\`.

```text
%LOCALAPPDATA%\.ayushman\
├── bin/
│   └── <pkg>.exe               # hard-linked executable
├── packages/
│   └── <pkg>/
│       └── <version>/
│           ├── <pkg>.exe
│           └── metadata.json   # package registry
└── metadata.json               # global registry
```

- `packages/` contains versioned, original executables
- `bin/` exposes the active version via hard links
- Global metadata references per-package metadata files

---

## PATH handling

Executables are exposed via `%LOCALAPPDATA%\.ayushman\bin`.

```powershell
# Verify that %LOCALAPPDATA%\.ayushman\bin is in your PATH
echo $env:PATH
# If not present, restart your terminal or re-login to see the updated PATH
```

AyushMan attempts to add: `%LOCALAPPDATA%\.ayushman\bin` to the user PATH on first run.

If the change does not take effect immediately, restart your terminal or re-login.

> This allows installed executables to be used globally from any terminal session.

> [!NOTE]
> If automatic PATH injection fails, manually add %LOCALAPPDATA%\.ayushman\bin to User Environment Variables.

---

## Package source & constraints

- Packages are downloaded **only** from this [author](https://github.com/JourneyCodesAyush)’s repositories
- The **latest release** is selected automatically
- ZIP assets must contain **binaries**
- No scripts, installers, or post-install hooks are executed
- Packages are expected to ship ready-to-run executables

---

## Commands

All commands are run using `ayushman`:

```bash
ayushman install pdf-toolkit
ayushman list
ayushman upgrade pdf-toolkit
ayushman uninstall pdf-toolkit
```

> [!WARNING]
> Danger zone ahead

> Remove 'AyushMan' from your system

```bash
ayushman purge
ayushman purge --dry-run # simulate without making changes
ayushman purge --force # skip confirmation prompt
```

All operations are safe to re-run and designed to be idempotent.

> [!TIP]
> After adding `%LOCALAPPDATA%\.ayushman\bin` to PATH, all installed executables behave like any other CLI tool.

---

## Scope

AyushMan is intentionally small in scope:

- No dependency resolution
- No source builds
- No cross-platform support
- No package ecosystem or central registry

AyushMan is designed for installing **trusted prebuilt Windows binaries** - not for managing software ecosystems.

---

## Philosophy

AyushMan focuses on **safe, versioned, prebuilt Windows binaries**.
No builds, no installers, no cross-platform abstraction — just install, run, and upgrade.

For a deeper explanation of why `AyushMan` works this way, its design principles, and the [author](https://github.com/JourneyCodesAyush)’s philosophy on package management, see [PHILOSOPHY.md](PHILOSOPHY.md).

---

## License

This project is licensed under the [**MIT License**](./LICENSE).

You’re free to use, modify, and distribute it.

> [!TIP]
> A tag or mention of [JourneyCodesAyush](https://github.com/JourneyCodesAyush) is always appreciated.
