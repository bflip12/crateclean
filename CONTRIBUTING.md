# Contributing to CrateClean

Thanks for helping out! This guide covers setting up, making a change and getting it merged. For coding conventions, see [docs/CODE_STYLE.md](docs/CODE_STYLE.md). For how the app fits together, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and for why it's built that way, the decision records in [docs/adr](docs/adr/README.md). What's planned is in [ROADMAP.md](ROADMAP.md).

## Ground rules

Every change has to keep these rules:

1. **Edit tags only.** Never rename, move or delete audio files, and never create files in the user's music folders. Rekordbox tracks files by path, so a moved file loses its cues, grids and playlists.
2. **Never touch BPM, key, rating, cue or DJ-software data**, or existing artwork the user hasn't approved replacing.
3. **Preview, back up, verify, undo.** Nothing is written without the user's approval, and every write goes through the write pipeline described in [ARCHITECTURE.md](docs/ARCHITECTURE.md#the-write-pipeline).
4. **Network access goes only to MusicBrainz, Cover Art Archive and Discogs.** No telemetry and no server.
5. **No new dependencies** without discussing them in an issue first. Each one is code that runs with access to the user's music, and its licence must be compatible with the GPL.

## Setting up

You need [uv](https://docs.astral.sh/uv/), which installs the right Python version for you, and `ffmpeg` for the test fixtures. On macOS:

```bash
brew install uv ffmpeg
```

On Windows:

```bash
winget install astral-sh.uv
```

```bash
winget install Gyan.FFmpeg
```

Then:

```bash
git clone https://github.com/bflip12/crateclean.git
cd crateclean
uv sync
```

`uv sync` creates a virtual environment in `.venv` with Python, the app's dependencies and the development tools, all pinned by `uv.lock`.

### Running the app

```bash
uv run crateclean
```

Point it at a copy of some music, not your real collection, while developing. The engine also has a command line, which is handy for trying the cleaning rules on a folder without the UI:

```bash
uv run crateclean-cli --help
```

### Running the tests

```bash
uv run pytest
```

The first run generates the audio fixtures in `tests/fixtures/generated/` with ffmpeg. The tests cover the golden cleaning cases, tag round trips on every format, the write pipeline, the matcher and a few UI smoke tests.

### Formatting, linting and types

```bash
uv run ruff format
```

```bash
uv run ruff check --fix
```

```bash
uv run pyright
```

CI runs `ruff format --check`, `ruff check` and `pyright`, and fails on any problem.

## Project layout

| Path | What's there |
|---|---|
| `src/crateclean/engine/` | Scanning, the cleaning rules, tag reading and writing with mutagen, the write pipeline, verification and art embedding. |
| `src/crateclean/match/` | The catalog-number and folder-name parsers and the release scorer. |
| `src/crateclean/apis/` | One client per service, plus the shared rate limiter and response cache. |
| `src/crateclean/store/` | The SQLite database: settings, scan cache, lookup cache, runs and the backup index. |
| `src/crateclean/cli.py` | The command line for the engine. |
| `src/crateclean/ui/` | The PySide6 app: windows, table models, background workers. The only package that imports Qt. |
| `tests/` | pytest tests. `tests/golden/` holds the cleaning rules' before-and-after cases as data, `tests/match/` the matcher cases, and `tests/fixtures/make_fixtures.py` builds the audio fixtures. |
| `packaging/` | The PyInstaller spec, the Windows installer script and the app icons. |
| `docs/` | Architecture and code style. |
| `docs/adr/` | Architecture decision records: why the app is built the way it is. |

## Making a change

Every change, including the maintainer's, reaches `main` through a pull request. `main` is protected:

- Nobody can push to it directly or force-push it.
- A pull request can only merge once CI passes, on a branch that's up to date with `main`, and all review conversations are resolved.
- Pull requests are squash-merged, so each one lands on `main` as one commit, and the branch is deleted afterwards.

The steps:

1. **Open an issue first** for anything bigger than a small fix, so we can agree on the approach before you spend time on it. Cleaning rules and matching especially, since a tweak that fixes one tag can break another.
2. **Branch from an up-to-date `main`.** Name the branch for what it does: `fix/keep-my-tag-slashes`, `feature/aiff-support`, `docs/…`, `ci/…`.
3. **Add or update tests.** Every cleaning or matching change needs a test with the real-world value that prompted it.
4. **Run `uv run ruff format`, `uv run ruff check`, `uv run pyright` and `uv run pytest`.**
5. **Update the docs** if behaviour changed: README for anything user-visible, `docs/ARCHITECTURE.md` for the design, `CHANGELOG.md` under **Unreleased**. A change that makes or reverses a significant design decision gets an ADR in `docs/adr/`, and shipping a roadmap item removes it from `ROADMAP.md`.
6. **Open a pull request** and fill in the template.

### Commit messages

- Write the subject in the imperative and keep it to about 72 characters, e.g. "Keep the slash in Rekordbox My Tag comments".
- In the body, explain *why* the change is needed, not just what it does. A reviewer should be able to understand the problem from the message alone.
- Make one logical change per commit. A formatting-only change goes in its own commit.

### Adding a promo phrase

Built-in promo phrases are in `src/crateclean/engine/promo_phrases.py`. A comment that matches one in full, after URLs are removed, is cleared. To add one:

1. Add the phrase, lowercase.
2. Add a row to `tests/golden/comments.json` with the real comment that prompted it, and one with a similar comment that must survive.
3. Run `uv run pytest`.

Phrases that only one person sees belong in their own list in Settings, not the built-in one.

### Adding a matcher test

Matcher cases live in `tests/match/`. Each case is a folder name, the tags of its tracks and the release that should (or shouldn't) match, with the expected score band. Please give metadata only; never attach audio files.

## Testing on Windows

Windows support is the last milestone on the roadmap ([ADR 0010](docs/adr/0010-macos-first.md)), so until then CI runs on macOS only. This is the plan for when it starts.

Most bugs that only happen on Windows are about files, not the UI: backslashes and drive letters, names that differ only in case, files locked by another program, paths over 260 characters, and unusual characters. They're covered in three layers.

### 1. CI, on every pull request

The Windows milestone adds a Windows job to the **CI** workflow, which runs the whole test suite and builds the Windows app. It's the first step of that milestone, followed by fixing whatever it finds. Tests for Windows-only behaviour, like a file another program has locked, are marked `@pytest.mark.windows` and are skipped on macOS. If you fix a Windows bug, add a test that fails on Windows without the fix.

### 2. A virtual machine, before each release

On an Apple silicon Mac, run Windows 11 for ARM in [VMware Fusion](https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion) (free for personal use), [UTM](https://mac.getutm.app) (free) or Parallels Desktop. Microsoft publishes the Windows 11 for ARM ISO, and it runs the normal Windows build through its built-in translation. Keep test music on the VM's own disk or a USB stick, not in a folder shared from the Mac, which behaves like a network drive.

Before each release, go through this checklist in the VM with the release candidate's installer:

- [ ] Download the installer from the GitHub pre-release, and get past SmartScreen with **More info › Run anyway**.
- [ ] Complete first-run onboarding.
- [ ] Add a music folder on `C:` and one on a USB stick, and scan both.
- [ ] Preview a cleanup, apply it, and check the report.
- [ ] Undo the run, and check the files match the originals.
- [ ] Apply while one of the files is open in another program, and check it's reported and the rest are written.
- [ ] Try a file with a path over 260 characters and one with non-Latin characters in its name.
- [ ] Uninstall, and check the app's data folder is left alone or removed as the uninstaller says.

### 3. Real Windows PCs, for release candidates

Before a release, someone who DJs on a Windows PC tries the release candidate on a copy of their music, including **Reload Tag** in Rekordbox. A VM can't fully stand in for a real PC with a real Rekordbox library.

## Releasing

Maintainers only:

1. Bump `version` in `pyproject.toml`.
2. In `CHANGELOG.md`, move the **Unreleased** entries under the new version with today's date, and remove shipped items from `ROADMAP.md`.
3. Make these changes on a `release/vX.Y.Z` branch and open a pull request titled "Release vX.Y.Z".
4. Push a release candidate tag (`vX.Y.Z-rc1`) from that branch. It becomes a pre-release. Install the macOS build from it and try it. Once Windows is supported, also go through [Testing on Windows](#testing-on-windows).
5. Once the pull request is merged, tag the merge commit on `main` as `vX.Y.Z` and push the tag.
6. The tag starts the **Release** workflow. It builds the app with PyInstaller, packs a DMG (and, once Windows is supported, a Windows installer), and publishes them to GitHub Releases with that changelog section as the notes.

Delete release candidates afterwards with `gh release delete vX.Y.Z-rc1 --cleanup-tag`.

### Signing

Builds are unsigned for now. On macOS they're ad-hoc signed, so the app runs on Apple silicon, and users click **Open Anyway** in **System Settings › Privacy & Security** on first launch. On Windows, SmartScreen shows "Windows protected your PC", and users click **More info › Run anyway**. The README and the release notes explain both.

## License

CrateClean is licensed under the [GNU General Public License v3.0 or later](LICENSE). By contributing, you agree that your contributions are licensed under the same terms.
