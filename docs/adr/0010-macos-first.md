# 0010. Ship for macOS first, and add Windows last

**Status:** Accepted

## Context

CrateClean is built to run on macOS and Windows ([0004](0004-python-and-qt.md)), but the maintainer develops on a Mac and has no Windows machine. Supporting Windows from the first pull request would mean fixing Windows-only CI failures before the app does anything useful, and every release would need a VM check.

## Decision

Build and release for macOS first. Windows support is the last roadmap milestone: Windows tests in CI, the Windows installer, and the checks in CONTRIBUTING.md's "Testing on Windows".

Until then, the code is still written to work on Windows: `pathlib` for paths, Python scripts rather than shell scripts, and nothing macOS-specific outside the UI's platform helper.

## Consequences

- Early milestones move faster, with one platform to build, test and release.
- Windows bugs pile up unseen until the Windows milestone, so it starts by turning on Windows CI and fixing whatever fails.
- Early releases reach only Mac users.
