# Roadmap

What's planned for CrateClean, roughly in order. There are no dates: it's a spare-time project, and things move when they're ready. Shipped work moves to [CHANGELOG.md](CHANGELOG.md).

Have an idea or need something on this list sooner? [Open a feature request](https://github.com/bflip12/crateclean/issues/new?template=feature_request.yml), or 👍 an existing one.

## Now

- **The cleaning engine.** Round-trip tests proving tags are written exactly ([ADR 0005](docs/adr/0005-tag-engine.md)), scanning, the cleaning rules with every golden case passing, and the backup, write, verify and undo pipeline, callable from the command line.
- **Builds for macOS.** A bare app that GitHub Actions packages into a DMG, so packaging works before the UI grows.

## Next

- **The app, and the first release for macOS.** Library table, cleanup preview, Apply, History with undo, and first-run onboarding.
- **Cover art from folder images,** with the review grid.

## Later

- **Cover art from MusicBrainz and Cover Art Archive,** with caching and rate limiting.
- **Cover art from Discogs,** with your own token.
- **AIFF and WAV files.**
- **Signed builds,** so the app opens without a security warning.
- **Windows.** Tests on Windows in CI, a Windows installer, and testing on real PCs with Rekordbox ([ADR 0010](docs/adr/0010-macos-first.md)).

## Not planned

These go against [the project's design decisions](docs/adr/README.md):

- Renaming, moving or organising files ([ADR 0002](docs/adr/0002-edit-tags-only.md)).
- Editing BPM, key, ratings or cue points ([ADR 0002](docs/adr/0002-edit-tags-only.md)).
- Writing to Rekordbox's database or XML ([ADR 0007](docs/adr/0007-never-write-rekordbox-data.md)).
- Accounts, a cloud backend or telemetry ([ADR 0006](docs/adr/0006-limited-network-access.md)).
