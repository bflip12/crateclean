# 0011. Compare untouched ID3 text frames by value, not by bytes

**Status:** Accepted

## Context

ADR [0005](0005-tag-engine.md) says frames CrateClean doesn't edit stay byte-identical. The round-trip tests showed that mutagen can't do that for ID3 text frames. When it saves a tag, it re-encodes every frame and ends each text value with a null terminator. A TBPM frame stored as `124` comes back as `124\0`, even though nothing changed it. The value, the encoding and the separators between multiple values all stay the same, and both ID3v2.3 and v2.4 allow the terminator. Every other frame (GEOB, PRIV, POPM, APIC and frames mutagen doesn't know) does stay byte-identical.

The options considered:

- **Accept the terminator,** and have the verifier compare text frames by their decoded values.
- **Write our own ID3 serializer** that copies untouched frames' original bytes. It would be exact, but it's new code in the riskiest part of the app, replacing a writer that's been used on real libraries.
- **Patch mutagen's text encoder.** It would be fragile, and could break on any mutagen release.

## Decision

Accept the terminator. For ID3 text frames (`T***`, `TXXX` and `COMM`), the verifier compares the frame id, encoding, descriptor, language and decoded values, ignoring one trailing terminator. Every other frame must still be byte-identical, along with the audio data and the ID3v1 footer.

## Consequences

- The engine keeps using mutagen's writer, which the round-trip tests cover.
- An untouched text frame can grow by a byte or two, so a file can differ from its backup outside the approved fields. The verifier allows exactly that and nothing else.
- Rekordbox has to read terminated text the same way. That's checked by hand before each release: run **Reload Tag** on files CrateClean has written, and compare BPM, key and comments (CONTRIBUTING.md, "Releasing").
- If a later mutagen release changes how text is encoded, the round-trip tests fail, and this ADR is reconsidered.
