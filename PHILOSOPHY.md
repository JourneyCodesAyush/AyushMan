# `ayuman` Philosophy

`ayuman` is intentionally minimal. It exists to solve **one simple problem**: installing prebuilt, trusted Windows binaries from the [author](https://github.com/JourneyCodesAyush)’s GitHub repositories, without adding unnecessary complexity.

## Design Principles

### 1. Windows-only

- I am a Windows user, so ayuman is built for Windows 10+ (`x86_64`).
- No cross-platform complications, no “one-size-fits-all” solutions.

### 2. Minimalism & Transparency

- Only installs prebuilt `.exe` files from ZIP releases.
- No dependency resolution, source builds, or post-install scripts.
- `~/.ayuman/bin` is added automatically to user PATH, ayuman does **NOT** modify system variables behind the scenes.

### 3. Trust-first approach

- Packages come **only** from the [author](https://github.com/JourneyCodesAyush)’s GitHub repositories.
- ZIPs must contain binaries only.
- This keeps the security model simple, explicit, and auditable.

### 4. Versioned & isolated installs

- Each package is stored versioned in `~/.ayuman/packages/<pkg>/<version>/`.
- Executables in `~/.ayuman/bin` are hard-linked for upgrade-safe usage.
- Metadata is stored both globally and per-package for predictable behavior.

### 5. Upgrade safety & idempotence

- Upgrading a package automatically does **NOT** remove older versions.
- All commands (`install`, `list`, `upgrade`, `uninstall`) are safe to re-run without side effects.

## What ayuman is **not**

- A general-purpose package manager
- A source builder
- A cross-platform installer
- A central package registry or ecosystem

ayuman is for **trusted, prebuilt Windows binaries**. It prioritizes **simplicity, predictability, and explicit trust** over convenience or universality.

## Installation philosophy

- `ayuman` itself can live anywhere; all data is stored in `~/.ayuman/`.
- Installed packages are added to user PATH after the first package installation.
- Executables on PATH behave like any other CLI tool.
- Only the latest release of a package is installed, reducing overhead and confusion.
