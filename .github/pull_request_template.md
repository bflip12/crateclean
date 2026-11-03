## What and why

<!-- What does this change, and what problem does it solve? Link the issue if there is one (e.g. "Fixes #12"). -->

## How it was tested

<!-- Tests added or updated, and anything you checked by hand in the app. -->

## Checklist

- [ ] `uv run ruff format`, `uv run ruff check` and `uv run pyright` are clean
- [ ] `uv run pytest` passes
- [ ] Every write goes through the write pipeline, and nothing creates, renames or deletes files in a music folder
- [ ] No protected fields (BPM, key, rating, cues, DJ-software frames) or unapproved artwork are touched
- [ ] No new network hosts or telemetry, and no new dependencies (or a GPL-compatible one agreed in an issue)
- [ ] The docs are updated (README, `docs/ARCHITECTURE.md`, `CHANGELOG.md`) if the behaviour changed
