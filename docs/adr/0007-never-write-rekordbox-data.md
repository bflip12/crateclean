# 0007. Never write to Rekordbox's database or XML

**Status:** Accepted

## Context

Rekordbox keeps its own copy of each track's tags in its database, so after CrateClean changes a file, Rekordbox still shows the old values. Writing to Rekordbox's database would update it directly, but the database is encrypted, undocumented and changes between versions, and a bad write could damage the user's whole collection.

## Decision

CrateClean never reads from or writes to Rekordbox's database or XML. After a run, it tells the user to select the affected tracks in Rekordbox and choose **Reload Tag**, and can export an `.m3u8` of those tracks so they're easy to find and select.

## Consequences

- No risk to the Rekordbox collection itself, and no breakage when Rekordbox updates.
- The user has one manual step after each run.
- Reload Tag replaces the values Rekordbox holds for those tracks with what's in the files, so the app should warn users who edit tags inside Rekordbox.
