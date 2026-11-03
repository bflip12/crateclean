# CrateClean

Clean junk out of your DJ music tags and find missing cover art, without breaking your Rekordbox library.

> CrateClean is in early development and there's no download yet. See the [roadmap](ROADMAP.md).

Downloaded tracks often carry junk in their tags: `GaGa www.electronicfresh.com`, `Visit https://label.bandcamp.com` in the comment, a promo line from the site it came from. CrateClean finds it, shows you exactly what it would change, and cleans it when you say so. It also finds covers for tracks with missing or low-res art, from the folder they're in, MusicBrainz and Cover Art Archive, or Discogs.

It's for macOS first, with Windows to follow. It's free and open source, and never moves or renames a file.

## Why it's Rekordbox-safe

Rekordbox links every track by its file path, and keeps your cues, grids and playlists on that link. CrateClean is built so that link never breaks:

- **It only edits tags.** Files are never renamed, moved or deleted, and nothing is created in your music folders.
- **It leaves your DJ data alone.** BPM, key, rating, cue points, Serato and Rekordbox data, and existing artwork are never touched.
- **You approve every change.** Nothing is written until you've reviewed it.
- **Every file is backed up first,** to CrateClean's own folder, not next to your music.
- **Every write is checked.** If anything other than the approved fields changed, the file is restored from its backup straight away.
- **Every run can be undone** from History.
- **It never touches Rekordbox's database.** After a run, select the changed tracks in Rekordbox, right-click and choose **Reload Tag**.

Still, back up your Rekordbox library before the first run: **File › Library › Backup Library**.

## Install

Coming with the first release.

The app isn't signed yet, so your system will warn you the first time you open it:

- **macOS:** open the app, then go to **System Settings › Privacy & Security** and click **Open Anyway**.
- **Windows** (coming later): when SmartScreen says "Windows protected your PC", click **More info**, then **Run anyway**.

## Discogs (optional)

CrateClean can also search Discogs for covers. It needs your own personal access token:

1. Sign in to Discogs and open [Settings › Developers](https://www.discogs.com/settings/developers).
2. Click **Generate new token** and copy it.
3. In CrateClean, paste it into **Settings › Discogs token**.

The token is stored encrypted on your computer and only ever sent to Discogs.

## Privacy

CrateClean has no accounts, no telemetry and no server. The only requests it makes are lookups for your releases to MusicBrainz, Cover Art Archive and, if you add a token, Discogs. It keeps to each service's rate limits, and caches results on your computer so a second run doesn't ask again.

## Credits

Cover art and release data come from [MusicBrainz](https://musicbrainz.org), [Cover Art Archive](https://coverartarchive.org) and, optionally, [Discogs](https://www.discogs.com). Data provided by Discogs is shown as such in the app.

CrateClean is written in Python, with [Qt for Python](https://doc.qt.io/qtforpython/) (LGPL) for the interface and [mutagen](https://github.com/quodlibet/mutagen) (GPL) for reading and writing tags.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Found junk CrateClean missed, or something it removed that it shouldn't have? [Report it](https://github.com/bflip12/crateclean/issues/new?template=wrong_cleanup.yml).

## License

[GPL-3.0-or-later](LICENSE). Rekordbox is a trademark of AlphaTheta Corporation. CrateClean isn't affiliated with or endorsed by AlphaTheta, MusicBrainz or Discogs.
