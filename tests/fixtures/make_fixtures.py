"""Generates the audio fixtures in `tests/fixtures/generated/` from silence.

`conftest.py` calls this before the tests run, so there's usually no need to run it by hand. To
rebuild the fixtures from scratch:

    uv run python -m tests.fixtures.make_fixtures --force

ffmpeg makes the audio and the cover image. The tags are written byte by byte by `id3_raw` and
`flac_raw`, or by ffmpeg for MP4, never by mutagen, so the fixtures don't depend on the code under
test. They hold the kinds of frames a DJ's files have: multi-value text, several comments, an
ID3v1 copy, BPM, key, rating, Serato and Rekordbox data, and cover art.
"""

import argparse
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from tests.fixtures import flac_raw, id3_raw
from tests.fixtures.id3_raw import UTF8, UTF16, apic, comm, geob, popm, priv, text, txxx

GENERATED_DIR = Path(__file__).parent / "generated"
COVER_SIZE = 600

TITLE = "Night Drive (Original Mix)"
ALBUM = "Test Album"
MAIN_COMMENT = "Main comment"
# Binary payloads stand in for DJ-software data, which must survive byte for byte.
SERATO_MARKERS = bytes(range(256)) * 2
REKORDBOX_PRIV = b"\x00\x01\x02rekordbox\xff\xfe"
UNKNOWN_FRAME = id3_raw.RawFrame("ZZRB", b"\x01\x02\x03 unknown frame data \xff")


def _ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def _silence(*args: str) -> list[str]:
    return ["-f", "lavfi", "-t", "1", "-i", "anullsrc=r=44100:cl=stereo", *args]


def _cover(work: Path) -> Path:
    path = work / "cover.png"
    color = f"color=c=0x336699:s={COVER_SIZE}x{COVER_SIZE}"
    _ffmpeg("-f", "lavfi", "-i", color, "-frames:v", "1", str(path))
    return path


def _mp3_audio(work: Path) -> bytes:
    """MPEG audio frames with no tags at all."""
    path = work / "silence.mp3"
    _ffmpeg(
        *_silence("-c:a", "libmp3lame", "-b:a", "128k"),
        "-write_id3v1",
        "0",
        "-id3v2_version",
        "0",
        "-map_metadata",
        "-1",
        "-fflags",
        "+bitexact",
        str(path),
    )
    return path.read_bytes()


def mp3_frames(version: int, png: bytes) -> list[id3_raw.RawFrame]:
    """The frames of the MP3 fixtures, in file order."""
    year = text("TYER", "2024") if version == 3 else text("TDRC", "2024-05-17")
    return [
        text("TIT2", TITLE),
        # Null-separated multi-value, as Rekordbox and Mp3tag write it.
        text("TPE1", "Artist One", "Artist Two"),
        # A slash that's part of the value, not a separator.
        text("TPE2", "Artist One/Artist Two"),
        text("TALB", ALBUM),
        year,
        text("TCOM", "Zoë Composer", encoding=UTF16 if version == 3 else UTF8),
        # iTunes writes sort frames into v2.3 files even though they're v2.4 frames.
        text("TSOP", "One, Artist"),
        text("TBPM", "124"),
        text("TKEY", "8A"),
        txxx("CATALOGNUMBER", "TEST001"),
        txxx("MOOD", "Dark", "Driving"),
        comm("", MAIN_COMMENT),
        comm("ID3v1 Comment", MAIN_COMMENT),
        comm("Notes", "Second comment", lang=b"deu"),
        popm("rekordbox@example.com", 196, 7),
        geob("Serato Markers_", "application/octet-stream", "", SERATO_MARKERS),
        priv("PeakValue", REKORDBOX_PRIV),
        apic(png),
        UNKNOWN_FRAME,
    ]


def _mp3(version: int) -> Callable[[Path, Path], None]:
    def build(work: Path, path: Path) -> None:
        png = _cover(work).read_bytes()
        v2 = id3_raw.build_v2(version, mp3_frames(version, png))
        v1 = id3_raw.build_v1(TITLE, "Artist One", ALBUM, "2024", MAIN_COMMENT, 0)
        path.write_bytes(v2 + _mp3_audio(work) + v1)

    return build


FLAC_COMMENTS = [
    ("TITLE", TITLE),
    ("ARTIST", "Artist One"),
    ("ARTIST", "Artist Two"),
    ("ALBUM", ALBUM),
    ("DATE", "2024"),
    ("DESCRIPTION", MAIN_COMMENT),
    ("COMMENT", "Second comment"),
    ("BPM", "124"),
    ("INITIALKEY", "8A"),
    ("RATING", "196"),
    ("SERATO_MARKERS_V2", "YXBwbGljYXRpb24vb2N0ZXQtc3RyZWFt"),
    ("CATALOGNUMBER", "TEST001"),
]


def _flac(work: Path, path: Path) -> None:
    plain = work / "silence.flac"
    _ffmpeg(*_silence("-c:a", "flac"), "-map_metadata", "-1", "-fflags", "+bitexact", str(plain))
    source = flac_raw.parse_flac(plain)
    stream_blocks = [
        b for b in source.blocks if b.type not in (flac_raw.VORBIS_COMMENT, flac_raw.PADDING)
    ]
    png = _cover(work).read_bytes()
    blocks = [
        *stream_blocks,
        flac_raw.vorbis_comment("reference libFLAC 1.4.3 20230623", FLAC_COMMENTS),
        flac_raw.picture(png, COVER_SIZE, COVER_SIZE),
        flac_raw.RawBlock(flac_raw.PADDING, b"\x00" * 1024),
    ]
    path.write_bytes(flac_raw.build_flac(blocks, source.audio))


def _m4a(work: Path, path: Path) -> None:
    cover = _cover(work)
    tags = {
        "title": TITLE,
        "artist": "Artist One",
        "album": ALBUM,
        "album_artist": "Artist One/Artist Two",
        "comment": MAIN_COMMENT,
        "date": "2024",
        "genre": "Deep House",
    }
    metadata = [arg for key, value in tags.items() for arg in ("-metadata", f"{key}={value}")]
    _ffmpeg(
        *_silence(),
        "-i",
        str(cover),
        "-map",
        "0",
        "-map",
        "1",
        "-c:a",
        "aac",
        "-c:v",
        "copy",
        "-disposition:v",
        "attached_pic",
        *metadata,
        str(path),
    )


FIXTURES: dict[str, Callable[[Path, Path], None]] = {
    "id3v23.mp3": _mp3(3),
    "id3v24.mp3": _mp3(4),
    "tags.flac": _flac,
    "tags.m4a": _m4a,
}


def make_fixtures(force: bool = False) -> Path:
    """Generate any fixtures that are missing and return the folder they're in.

    Args:
        force: Regenerate every fixture, even ones that already exist.

    Raises:
        RuntimeError: ffmpeg isn't installed.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "The tests need ffmpeg to generate their audio fixtures. Install it with "
            "'brew install ffmpeg' on macOS or 'winget install Gyan.FFmpeg' on Windows."
        )
    GENERATED_DIR.mkdir(exist_ok=True)
    for name, build in FIXTURES.items():
        path = GENERATED_DIR / name
        if force or not path.exists():
            with tempfile.TemporaryDirectory() as work:
                build(Path(work), path)
    return GENERATED_DIR


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the audio fixtures for the tests.")
    parser.add_argument("--force", action="store_true", help="regenerate every fixture")
    print(make_fixtures(force=parser.parse_args().force))
