# Code style

These are the conventions for CrateClean's Python code. Most of the formatting is automatic. The rest is about keeping the code small, readable and safe for the user's files.

## Formatting and checks

- The code is formatted and linted with **ruff**, and type-checked with **pyright**. Settings are in [`pyproject.toml`](../pyproject.toml): 100-column lines, sorted imports.
- Run `uv run ruff format` and `uv run ruff check --fix` before committing. CI runs `ruff format --check`, `ruff check` and `pyright`, and fails on any problem.
- Don't hand-align code; the formatter decides line breaks. If its output reads badly, restructure the code (pull out a local, split the expression) rather than fighting it.
- `engine`, `match`, `apis` and `store` are checked in pyright's strict mode. Don't add `# type: ignore` without a comment saying why.

## Structure

- **Logic goes in `engine`, `match`, `apis` and `store`.** They must not import Qt, so they can be unit tested and run from the command line. If something can be unit tested, it belongs there.
- **The UI stays thin.** Widgets display state and call into the core; a widget shouldn't make a decision that a test would want to cover. Large tables use Qt's model/view classes (`QAbstractTableModel`), not item widgets.
- **The GUI thread never waits.** Scanning, writing, hashing and network requests run in workers (`QThreadPool` or a `QThread`) and report progress and results with signals.
- **Each module starts with a docstring** of one or two lines saying what it's for and anything non-obvious about it, e.g. "Never strips the slash in `/*` or `*/`: Rekordbox My Tag comments use it". ruff enforces this.
- Name modules for their job in snake_case (`clean_rules.py`, `rate_limit.py`). Small helpers live next to their only caller.

## Naming

- Follow [PEP 8](https://peps.python.org/pep-0008/): `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants. A leading underscore marks anything private to its module.
- Public functions use full, descriptive names: `clean_comment`, `parse_catalog_number`. Short names are fine for locals in a tight scope.
- Domain terms are used consistently:

  | Term | Meaning |
  |---|---|
  | *music folder* | a folder the user added; in UI copy and code |
  | *field* | Title, Artist, Album or Comment, independent of tag format |
  | *frame* | a format-specific tag entry (ID3 frame, Vorbis comment, MP4 atom) |
  | *change* | one proposed edit to one field of one file |
  | *run* | one Apply: its changes, backups and report |
  | *release* | a group of tracks that should share one cover: same folder and album tag |
  | *candidate* | a possible cover for a release, from one source |

## Documentation

- **Every public function, class and method in the core packages has a docstring**, in Google style. Start with a one-line summary, then add only what a caller needs: units (pixels, 0–1 scores), what `None` or an empty string means, and side effects. ruff enforces this.
- Type hints say what the types are; the docstring doesn't repeat them.
- Plain comments explain *why*, not what. If a comment just restates the code, delete it.
- Behaviour changes update [ARCHITECTURE.md](ARCHITECTURE.md) in the same PR.

## Safety rules

These protect the user's music and Rekordbox library, and are checked in review:

- **Only `crateclean.engine.write` saves tags**, and only through the write pipeline. Nothing else calls a mutagen `save()` or opens a music file for writing.
- **Never create, rename, move or delete files in a music folder.** Backups, caches, exports and temporary files go in the app's data folder.
- **Never touch protected fields**: BPM, key, rating, cues, GEOB/PRIV frames and their FLAC and MP4 equivalents. The verifier treats any change to them as a failure.
- **Only `crateclean.apis` makes network requests**, only to the three allowed hosts, and only through the rate limiter.
- **Never log or display the Discogs token.** Read it from `keyring` only when making a request.
- **Don't add dependencies** without an issue first, and check the licence is GPL-compatible. Prefer the standard library.

## Python

- **Type hints everywhere.** Use `X | None`, built-in generics (`list[str]`) and `collections.abc` types. Avoid `Any`; parse untrusted data (tags, folder names, JSON from APIs, the database) at the boundary and pass typed values inward.
- **Prefer plain data.** Values passed between layers are `@dataclass(frozen=True, slots=True)` or `enum` types.
- **Paths are `pathlib.Path`**, never strings joined by hand. Compare paths after normalising them, and remember Windows paths are case-insensitive.
- **Text from tags is never assumed to be clean.** It can contain null characters, odd encodings and trailing whitespace that matters; don't `strip()` a value the rules haven't decided to change.
- **Errors:**
  - Core functions raise exceptions whose message is ready to show to the user, defined in each package's `errors.py`.
  - The UI shows the message as is. It doesn't wrap it in "Error:" or add an error code.
  - Failures that aren't the user's concern (a corrupt cache entry, an unreadable thumbnail) fall back quietly to a sensible default and are logged.
  - A per-file failure during a run is recorded in the run's report and doesn't stop the other files.
  - Never use a bare `except:`. Catch the narrowest exception that makes sense.
- **Logging** uses the `logging` module, never `print`. Logs never contain the Discogs token, and only contain paths at debug level.

## Qt

- Use PySide6, with `from PySide6.QtWidgets import …` style imports.
- Connect signals to methods or small lambdas, never to code that does slow work.
- Every action works from the keyboard, and the review grid's shortcuts (J/K to move, A to approve, S to skip) are shown in the UI.
- Follow the system's light or dark appearance. Don't hard-code colours outside the one palette module.

## UI copy

- Write in plain, friendly sentences, in sentence case everywhere, buttons included: "Write tags to 406 files", "Choose folder…".
- Name destructive actions plainly, with the count: "Write tags to 406 files", not "Apply" or "OK".
- Use an ellipsis (…) on a command that opens a dialog.
- Use each platform's own words where they differ: Finder or File Explorer, ⌘ or Ctrl, Settings or Options. Keep these in one helper rather than scattered through the UI.
- Error messages say what happened, then what to do. For example: "Couldn't write to 'Track.mp3' because another app has it open. Close Rekordbox and try again."
- Say "music folder", not "library", when talking about the user's files. "Rekordbox library" means Rekordbox's own collection.

## Tests

- Tests use **pytest**, and UI smoke tests use **pytest-qt**.
- Name each test after the behaviour it checks: `test_keeps_my_tag_slashes`, `test_drops_a_v1_copy_that_is_a_prefix_of_the_main_comment`.
- The golden cleaning cases live as data in `tests/golden/` and run through one parametrised test. Add a row, not a new test, for a new case.
- Tag round-trip tests run on generated fixtures and compare every frame before and after.
- Every cleaning or matcher fix comes with a test using the real-world value that exposed it.
- Tests never touch files outside a temporary copy of the fixtures (`tmp_path`).
- Tests that only make sense on one platform are marked `@pytest.mark.windows` or `@pytest.mark.macos`.

## Scripts

- Scripts are Python, in `scripts/` or next to what they serve, and run with `uv run`, so they work the same on macOS and Windows. Don't write shell scripts for anything CI runs on Windows.
- A module docstring says what the script does and how to call it.
