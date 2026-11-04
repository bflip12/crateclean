# 0005. Use mutagen as the tag engine, guarded by round-trip tests

**Status:** Accepted. Byte-identical ID3 text frames are superseded by [0011](0011-id3-text-terminators.md).

## Context

ADR [0003](0003-preview-backup-verify-undo.md) depends on the tag engine writing exactly what it's asked to and nothing else. The prototype found the cases that go wrong: ID3v2.3 upgraded to v2.4, null-separated multi-values joined with `/`, COMM frames keyed by language instead of descriptor, and truncated ID3v1 copies. The prototype uses mutagen and handles all of them, after some fixes.

## Decision

Use mutagen. Before the engine is built on it, write automated round-trip tests on generated fixtures for each case the app depends on:

- ID3v2.3 is read and written without being upgraded to v2.4.
- Null-separated multi-value text frames in v2.3 (TPE1, TXXX) survive unchanged.
- COMM frames keep their descriptor and language, and one can be deleted without touching the others.
- An ID3v1 footer is updated or left consistent.
- FLAC Vorbis comments and PICTURE blocks, and MP4 `©nam`, `©ART`, `©alb`, `©cmt` and `covr` atoms, are read and written.
- GEOB, PRIV and other frames CrateClean doesn't edit stay byte-identical.

These tests stay in the suite and run on every pull request on both platforms.

## Consequences

- The engine starts from code that's already worked on a real library.
- mutagen is GPL-licensed, so CrateClean is too ([0009](0009-gpl-licence.md)).
- mutagen converts ID3v2.3 frames to v2.4 in memory on load unless told not to, so how files are loaded and saved has to be deliberate, and the round-trip tests are what prove it.
- If a round-trip test can't be made to pass, that's reported and decided in a new ADR, not worked around.
