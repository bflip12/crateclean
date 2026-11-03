# 0003. Preview, back up, verify and undo every write

**Status:** Accepted

## Context

Tag libraries are inconsistent, and tag writers have subtle bugs: some upgrade ID3v2.3 to v2.4, some join null-separated multi-values with `/`, and some rewrite frames they don't understand. A user may run CrateClean over thousands of files they care about, so a bug has to be caught before it reaches them, and reversible if it does.

## Decision

- Nothing is written until the user has reviewed the changes and clicked Apply.
- Every file is backed up in full before it's written.
- Every write is verified: all frames and a hash of the audio data are compared before and after. If anything outside the approved fields changed, the file is restored from its backup at once and reported.
- Every run can be undone from History.
- Files are written in place, not through a temporary file and rename, so nothing is ever created in a music folder and the file's creation date doesn't change.

## Consequences

- A write bug shows up as a reported, restored file instead of a silently damaged one.
- Backups take as much space as the files they cover. A large art run can mean gigabytes, so the app shows the space needed before Apply and keeps only the last few runs by default.
- An in-place write that's interrupted (a crash, a pulled drive) can leave a damaged file; the backup is how it's recovered.
