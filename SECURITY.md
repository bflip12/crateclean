# Security policy

## Supported versions

Security fixes go into the latest release and `main`.

## Reporting a vulnerability

Please **don't open a public issue** for security problems. Instead, report them privately through GitHub: on the repository's **Security** tab, choose **Report a vulnerability**.

Include what you found, how to reproduce it, and what an attacker could do with it. You'll get a reply within a week, and a fix or a plan within 30 days of the report being confirmed.

## Scope

CrateClean runs locally and writes to the user's audio files, so the areas most worth a look are:

- Parsing untrusted input: tags and embedded images in audio files, folder names, and responses and images from MusicBrainz, Cover Art Archive and Discogs.
- Anything that could make CrateClean write outside the approved fields, create, rename or delete files in a music folder, or write anywhere other than its own data folder.
- The Discogs token leaking into logs, the database, the cache or any request other than one to Discogs.
- Requests going anywhere other than the three services, or following a redirect somewhere unexpected.
