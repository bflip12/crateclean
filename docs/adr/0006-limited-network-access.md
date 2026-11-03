# 0006. Talk only to MusicBrainz, Cover Art Archive and Discogs

**Status:** Accepted

## Context

Finding cover art needs online lookups. But a tool with access to someone's whole music collection shouldn't send anything anywhere it doesn't need to, and a public repository can't hold API secrets.

## Decision

- The app makes requests only to MusicBrainz, Cover Art Archive and, if the user adds their own personal access token, Discogs. Requests go through clients that respect each service's rate limits and identify the app with a User-Agent that gives the repository URL as the contact.
- No telemetry, analytics, crash reporting or update server, and no server of our own.
- No consumer key or secret is shipped. The Discogs token is stored in the system's password store (Keychain on macOS, Credential Manager on Windows) through `keyring`.
- Responses are cached only on the user's machine; there's no shared cache.

## Consequences

- Users can see exactly what leaves their machine: search queries for their releases, and image downloads.
- Without a network connection, folder images still work; online lookups wait.
- There's no automatic update check, so users learn about new versions from the website or GitHub.
- Each Discogs user has to create their own token, which the README explains.
