# 0004. Build with Python and Qt for macOS and Windows

**Status:** Accepted

## Context

Rekordbox runs on macOS and Windows, and many DJs use Windows, so the app needs both from one codebase. The riskiest part of the app is writing tags without damaging anything else in the file, and the cleaning rules come from a Python prototype that's been run against a real library. The options considered:

- **Electron with TypeScript:** a web UI, but the rules would have to be ported, and the JavaScript tag libraries are less proven on the ID3v2.3 cases the prototype hit. Falling back to the prototype's engine would mean a Python sidecar anyway.
- **Tauri with Rust:** small and fast, but a new language, a port of everything, and a younger tag library. The app's speed is limited by disks and API rate limits, not by its own code.
- **A native app for each platform:** the tag engine would be written twice, and the two would have to behave identically on the riskiest code.
- **Python with Qt:** the prototype's rules and tag engine carry over directly, with a mature cross-platform UI toolkit.

## Decision

Write the app in Python with a Qt interface (PySide6). Use uv to manage Python, dependencies and the lockfile; pytest for tests; ruff for formatting and linting; pyright for type checking; and PyInstaller to package it.

## Consequences

- One language and one process. The cleaning rules and the golden tests come straight from the prototype.
- Qt gives native-looking controls and fast large tables on both platforms, but the app looks like a desktop app rather than a web app.
- The download is around 80–150 MB, because it bundles Python and Qt.
- Packaging Python is fiddly, so it's set up early, before most of the UI.
- PyInstaller executables are sometimes flagged by antivirus on Windows. If that becomes a problem, Nuitka is the fallback.
