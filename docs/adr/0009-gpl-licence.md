# 0009. License the project under GPL-3.0-or-later

**Status:** Accepted

## Context

CrateClean bundles mutagen ([0005](0005-tag-engine.md)), which is licensed GPL-2.0-or-later. Anyone distributing an app that includes it has to distribute the whole app under GPL-compatible terms, with its source available. A permissive licence like MIT would be fine for the source code on its own, but not for the downloads that bundle mutagen. PySide6 is LGPL-3.0, which is compatible with GPL-3.0.

## Decision

License CrateClean under the GNU General Public License, version 3 or later.

## Consequences

- The downloads and the source are under one licence, with nothing to explain.
- Anyone can use, change and share CrateClean, but versions they distribute must stay open source under the GPL.
- Every new dependency must have a GPL-3.0-compatible licence. MIT, BSD, Apache-2.0, LGPL and GPL are fine.
- The About screen and the README credit mutagen and Qt with their licences.
