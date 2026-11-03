# Architecture decision records

Each file here records one decision that shapes CrateClean: the situation, what was decided, and what follows from it. They explain *why* the code and the project look the way they do. [ARCHITECTURE.md](../ARCHITECTURE.md) explains *how* it works today.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-record-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-edit-tags-only.md) | Edit tags only, and never touch DJ data | Accepted |
| [0003](0003-preview-backup-verify-undo.md) | Preview, back up, verify and undo every write | Accepted |
| [0004](0004-python-and-qt.md) | Build with Python and Qt for macOS and Windows | Accepted |
| [0005](0005-tag-engine.md) | Use mutagen as the tag engine, guarded by round-trip tests | Accepted |
| [0006](0006-limited-network-access.md) | Talk only to MusicBrainz, Cover Art Archive and Discogs | Accepted |
| [0007](0007-never-write-rekordbox-data.md) | Never write to Rekordbox's database or XML | Accepted |
| [0008](0008-unsigned-releases.md) | Ship unsigned builds from GitHub Releases | Accepted |
| [0009](0009-gpl-licence.md) | License the project under GPL-3.0-or-later | Accepted |
| [0010](0010-macos-first.md) | Ship for macOS first, and add Windows last | Accepted |

## Writing a new one

Copy [template.md](template.md) to the next number with a short slug, e.g. `0011-aiff-support.md`, fill it in, and add it to the table above in the same pull request as the change it describes.

- Keep it short: a reader should get the decision in a minute.
- Don't edit an accepted ADR's decision. If it changes, write a new ADR that supersedes it, and set the old one's status to `Superseded by [00NN](00NN-slug.md)`.
- Statuses: Proposed, Accepted, Superseded, Deprecated.
