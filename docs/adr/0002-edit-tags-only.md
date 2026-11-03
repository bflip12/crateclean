# 0002. Edit tags only, and never touch DJ data

**Status:** Accepted

## Context

Rekordbox links every track in its collection by file path. Cue points, beatgrids, playlists and play history all hang off that path, so moving or renaming a file loses them. Other DJ software stores its own data inside the tags: Serato keeps cues and grids in GEOB frames, and many tools write BPM, key and rating. A tag cleaner that "tidies up" too much can do real damage to someone's sets.

## Decision

CrateClean edits the text of four fields (Title, Artist, Album and Comment) and adds front-cover art. It never renames, moves or deletes audio files, and never creates files inside music folders. It never changes BPM, key, rating, cue or DJ-software frames, and never replaces existing artwork unless the user approves replacing low-res art.

## Consequences

- File paths never change, so Rekordbox's links stay intact.
- Features like renaming files to match their tags, organising folders or fixing BPM are out of scope.
- Backups, caches and exports go in the app's data folder, which uses more space on the system drive.
