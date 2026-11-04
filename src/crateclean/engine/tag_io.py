"""Loads tags from MP3, FLAC and M4A files without changing their form in memory.

ID3 tags are loaded untranslated, so ID3v2.3 frames stay v2.3 frames, and without merging the
ID3v1 footer into them, so saving can't copy v1 values into the v2 tag. The round-trip tests in
`tests/roundtrip/` guard these options; don't change them without those tests passing.
"""

from pathlib import Path

from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp4 import MP4

ID3V1_SIZE = 128


def load_id3(path: Path) -> ID3:
    """Load an MP3 file's ID3v2 tag exactly as it's stored."""
    return ID3(path, translate=False, load_v1=False)


def read_id3v1(path: Path) -> bytes | None:
    """The file's 128-byte ID3v1 footer, or `None` if it has none."""
    with path.open("rb") as file:
        if file.seek(0, 2) < ID3V1_SIZE:
            return None
        file.seek(-ID3V1_SIZE, 2)
        footer = file.read(ID3V1_SIZE)
    return footer if footer.startswith(b"TAG") else None


def load_flac(path: Path) -> FLAC:
    """Load a FLAC file's Vorbis comments and pictures."""
    return FLAC(path)


def load_mp4(path: Path) -> MP4:
    """Load an M4A file's iTunes metadata atoms."""
    return MP4(path)
