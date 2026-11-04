"""Saves tags. The only module that writes to music files.

The functions here are the low-level saves. The write pipeline (back up, write, verify, restore)
will be built on them in this module, and nothing else may call them. The options they pass are
what keeps each file's format; the round-trip tests in `tests/roundtrip/` guard them.
"""

from pathlib import Path

from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp4 import MP4

from crateclean.engine.errors import UnsupportedTagError
from crateclean.engine.tag_io import ID3V1_SIZE, read_id3v1

# mutagen's own value for "rewrite the ID3v1 footer if the file has one, never add one".
_UPDATE_EXISTING_V1 = 1


def save_id3(tags: ID3, path: Path, v1_footer: bytes | None) -> None:
    """Save an ID3v2 tag in its original version, with null-separated multi-values.

    mutagen rebuilds the ID3v1 footer from the v2 frames and leaves its comment empty, so the
    footer is then overwritten with `v1_footer`.

    Args:
        tags: A tag loaded with `tag_io.load_id3`.
        path: The file to write.
        v1_footer: The 128-byte ID3v1 footer to keep or write. Ignored if the file has no
            footer; `None` keeps whatever mutagen writes.

    Raises:
        UnsupportedTagError: The tag is ID3v2.2, which mutagen can only write as v2.3 or v2.4.
    """
    # mutagen's type hints leave parts of its API unknown, which pyright's strict mode flags.
    major: int = tags.version[1]  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if major not in (3, 4):
        raise UnsupportedTagError(
            f"'{path.name}' has an ID3v2.{major} tag, which CrateClean can't write without "
            "converting it. It's been left unchanged."
        )
    if v1_footer is not None and (len(v1_footer) != ID3V1_SIZE or not v1_footer.startswith(b"TAG")):
        raise ValueError("v1_footer must be a 128-byte ID3v1 tag")
    # mutagen documents v23_sep=None as "use null separators", but annotates it as str only.
    tags.save(  # pyright: ignore[reportUnknownMemberType]
        path,
        v1=_UPDATE_EXISTING_V1,
        v2_version=major,
        v23_sep=None,  # pyright: ignore[reportArgumentType]
    )
    if v1_footer is not None and read_id3v1(path) is not None:
        with path.open("r+b") as file:
            file.seek(-ID3V1_SIZE, 2)
            file.write(v1_footer)


def save_flac(tags: FLAC) -> None:
    """Save a FLAC file's Vorbis comments and pictures back to the file it was loaded from."""
    tags.save()  # pyright: ignore[reportUnknownMemberType]


def save_mp4(tags: MP4) -> None:
    """Save an M4A file's metadata atoms back to the file it was loaded from."""
    tags.save()  # pyright: ignore[reportUnknownMemberType]
