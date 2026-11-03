# 0001. Record architecture decisions

**Status:** Accepted

## Context

CrateClean has rules that look arbitrary without their history: never create a temporary file next to the music, keep ID3v2.3 tags at v2.3, never clean a truncated ID3v1 comment on its own. If they're only explained in commit messages, they're easy to miss and easy to undo by accident.

## Decision

Record each significant decision as a short architecture decision record (ADR) in `docs/adr/`, numbered in order, with its context, the decision and its consequences.

## Consequences

- New contributors can find out why something is the way it is before changing it.
- Reversing a decision means writing a new ADR, which makes the change deliberate.
- It's one more file to write for a big change. Small changes don't need one.
