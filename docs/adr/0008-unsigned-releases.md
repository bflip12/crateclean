# 0008. Ship unsigned builds from GitHub Releases

**Status:** Accepted

## Context

Signing a macOS app properly needs a paid Apple Developer account, and signing a Windows app needs a certificate or a signing service. Without them, both systems warn users on first launch.

## Decision

Publish builds to GitHub Releases from a GitHub Actions workflow when a version tag is pushed. PyInstaller builds the app on a macOS runner, and it's packed into a DMG. A Windows installer is added in the Windows milestone ([0010](0010-macos-first.md)). macOS builds are ad-hoc signed, which Apple silicon needs to run the app at all. The README and the release notes explain how to get past Gatekeeper and SmartScreen.

Apple silicon Macs come first. Whether to add an Intel Mac build is decided when packaging is set up.

## Consequences

- Releases cost nothing and are reproducible from the repository.
- Users see a warning on first launch and need an extra step, which some won't take.
- Switching to signed builds later needs only secrets and workflow changes, recorded in a new ADR.
