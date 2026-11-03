# Architecture

How CrateClean works. For *why* it's built this way, see the [decision records](adr/README.md).

> This describes the planned design. Update each section as it's built, and mark anything not built yet as planned.

## Modules and threads

CrateClean is a Python app with a Qt (PySide6) interface. The code is split so everything that touches files or the network can be tested without Qt:

| Package | Does | Imports Qt? |
|---|---|---|
| `engine` | Scanning, cleaning rules, reading and writing tags with mutagen, the write pipeline, art embedding | No |
| `match` | Catalog-number and folder-name parsing, release scoring | No |
| `apis` | MusicBrainz, Cover Art Archive and Discogs clients, the rate limiter, the response cache | No |
| `store` | The SQLite database | No |
| `cli` | A command line over the engine, for testing and scripting | No |
| `ui` | Windows, table models and background workers | Yes |

The GUI thread only draws and handles input. Scanning, writing, hashing and lookups run on worker threads and report progress with Qt signals. The UI decides where the app's data folder is (`QStandardPaths.AppLocalDataLocation`) and passes it to the core packages, so they never ask Qt for anything.

## Data flow

1. **Scan.** The user adds music folders. The worker walks them for `.mp3`, `.flac` and `.m4a` files (skipping `._*` AppleDouble files), reads each file's fields and art dimensions, and sends them back in batches with progress. Results are cached by path, size and modification time, so rescans only read changed files.
2. **Clean.** The cleaning rules run over every track's fields and produce a list of changes. The preview shows them as a before/after diff, and the user switches changes on or off per track or per rule.
3. **Art.** Tracks with no art, or art below the minimum size, are grouped into releases. Each release gets one lookup: folder image first, then MusicBrainz and Cover Art Archive, then Discogs if the user added a token. The review grid shows the candidates, and the user approves them.
4. **Apply.** The approved changes go through the write pipeline as one run.
5. **Reload in Rekordbox.** The app tells the user to select the affected tracks in Rekordbox and choose **Reload Tag**, and can export an `.m3u8` of them to the app's data folder to make that easier.

## The write pipeline

Every write, for every file, goes through these steps in `crateclean.engine.write`:

1. **Check** that the file hasn't changed since it was scanned (size, modification time and content hash).
2. **Back up** the whole file to `<userData>/backups/<runId>/`, mirroring its path relative to its music folder.
3. **Snapshot** every frame (id, descriptor, decoded value), the raw bytes of frames CrateClean doesn't understand, and a hash of the audio data.
4. **Write** the approved changes in place, keeping the tag version and multi-value separators.
5. **Verify** by taking the snapshot again. Only the approved fields may differ. Unknown frames must be byte-identical, and the audio hash must match.
6. **Restore** from the backup straight away if verification fails, and record the file as a problem in the run's report.

Files are written in place rather than through a temporary file and rename, because the rules forbid creating files in music folders and a rename changes the file's creation date. The backup is what makes an interrupted write recoverable.

## Cleaning rules

The rules are ported from a Python prototype that was run against a real library. They target Title, Artist, Album and Comment (FLAC's `DESCRIPTION` counts as Comment).

- **URLs** are removed: an optional `url:` prefix, `http(s)://…`, `www.…`, and bare domains on a fixed list of endings.
- **Promo phrases:** a comment that matches one in full after URLs are removed is cleared. The built-in list is extended by the user's own list in Settings.
- **Tidying** happens only to values where a URL was found: empty brackets, leading and trailing separators (never the `/` in `/*` or `*/`), a leading "Visit", wrapping quotes, and extra whitespace. Values with no URL are returned exactly as they were.
- **Empty results:** an empty Title, Artist or Album frame is deleted, and an empty Comment is cleared.
- **MP3 comments:** only `COMM` frames with the descriptor `""` or `"ID3v1 Comment"` are cleaned. Frames are keyed by descriptor, not language.
- **ID3v1 copies:** a truncated 30-character copy of the main comment is replaced with the cleaned main comment truncated to 30, never cleaned on its own.

The full before-and-after cases are in `tests/golden/`, and they're the spec.

## Art matching

Planned. Signals, strongest first: catalog number (parsed from folder names like `(ES0040)` or `[OYSTER52]`, ignoring years and words like `WEB`), artist and release title, track count and year. Text is normalised and compared with token-set similarity; a catalog-number match is a near-decisive bonus.

| Score | Shown as |
|---|---|
| 0.9 or more | Suggested, and included in bulk approve |
| 0.6 to 0.9 | Needs review |
| Under 0.6 | Not shown; the release is listed as having no confident match |

Folder images are used only when the folder holds a single release (every track has the same non-empty album tag), the image is at least the minimum size, and it's the only image or the only one named like `cover`, `folder` or `front`.

## Network clients

Planned. One module per service in `crateclean.apis`, sharing a rate limiter and a response cache. Requests run on worker threads.

| Service | Limit | Notes |
|---|---|---|
| MusicBrainz | About 1 request a second, with jitter; exponential backoff on 503 | User-Agent `CrateClean/<version> ( <repo URL> )` |
| Cover Art Archive | 2–3 requests at once | `250` thumbnails for previews, `1200` for embedding |
| Discogs | Throttled against the rate-limit headers (60 a minute with a token) | Only with the user's own token; image URLs used exactly as returned |

Responses, including "no match", are cached in SQLite on the user's machine. Lookups run in the background while the user reviews what's already in. Without a network connection, folder-image matching still works.

## Storage

Everything lives in the app's data folder: `~/Library/Application Support/CrateClean` on macOS and `%LOCALAPPDATA%\CrateClean` on Windows.

| What | Where |
|---|---|
| Settings, scan cache, lookup cache, runs and the backup index | `crateclean.db` (SQLite) |
| Backups | `backups/<runId>/…` |
| Exported `.m3u8` files | `exports/` |
| The Discogs token | The system's password store (Keychain or Windows Credential Manager), through `keyring` |

## History and undo

Each Apply creates a run with its timestamp, type (clean or art), and each file's before and after values. Undo restores the backups, newest run first, and warns when a file has changed since the run. Old runs are pruned according to the retention setting (by default the last 10), and Settings shows the disk space backups use.
