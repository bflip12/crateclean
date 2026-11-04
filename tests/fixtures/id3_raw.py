"""Builds and parses ID3v2.3/2.4 and ID3v1 tags byte by byte, without mutagen.

The fixtures are built with this, and the round-trip tests read files back with it, so neither
depends on the library under test. Only what the fixtures use is supported: no unsynchronisation,
extended headers, compression or frame flags.
"""

import struct
from dataclasses import dataclass
from pathlib import Path

LATIN1 = 0
UTF16 = 1
UTF8 = 3  # ID3v2.4 only


@dataclass(frozen=True, slots=True)
class RawFrame:
    """One ID3v2 frame as it is in the file: its id, flag bytes and payload."""

    id: str
    data: bytes
    flags: bytes = b"\x00\x00"


@dataclass(frozen=True, slots=True)
class RawMp3:
    """An MP3 file split into its ID3v2 tag, audio and ID3v1 footer."""

    version: int
    frames: list[RawFrame]
    padding: int
    audio: bytes
    v1: bytes | None


def _encode(text: str, encoding: int) -> bytes:
    if encoding == LATIN1:
        return text.encode("latin-1")
    if encoding == UTF16:
        return text.encode("utf-16")  # with a BOM, as ID3 requires
    return text.encode("utf-8")


def _terminator(encoding: int) -> bytes:
    return b"\x00\x00" if encoding == UTF16 else b"\x00"


def _join(values: list[str], encoding: int) -> bytes:
    return _terminator(encoding).join(_encode(value, encoding) for value in values)


def text(frame_id: str, *values: str, encoding: int = LATIN1) -> RawFrame:
    """A text frame. Several values are joined with null separators."""
    return RawFrame(frame_id, bytes([encoding]) + _join(list(values), encoding))


def txxx(description: str, *values: str, encoding: int = LATIN1) -> RawFrame:
    """A user-defined text frame."""
    return RawFrame(
        "TXXX",
        bytes([encoding])
        + _encode(description, encoding)
        + _terminator(encoding)
        + _join(list(values), encoding),
    )


def comm(description: str, value: str, lang: bytes = b"eng", encoding: int = LATIN1) -> RawFrame:
    """A comment frame."""
    return RawFrame(
        "COMM",
        bytes([encoding])
        + lang
        + _encode(description, encoding)
        + _terminator(encoding)
        + _encode(value, encoding),
    )


def geob(description: str, mime: str, filename: str, data: bytes) -> RawFrame:
    """A general encapsulated object, as Serato stores cues and grids."""
    return RawFrame(
        "GEOB",
        b"\x00"
        + mime.encode()
        + b"\x00"
        + filename.encode()
        + b"\x00"
        + description.encode()
        + b"\x00"
        + data,
    )


def priv(owner: str, data: bytes) -> RawFrame:
    """A private frame."""
    return RawFrame("PRIV", owner.encode() + b"\x00" + data)


def popm(email: str, rating: int, count: int) -> RawFrame:
    """A popularimeter (rating) frame."""
    return RawFrame("POPM", email.encode() + b"\x00" + bytes([rating]) + struct.pack(">I", count))


def apic(png: bytes, picture_type: int = 3) -> RawFrame:
    """An attached picture, front cover by default."""
    return RawFrame("APIC", b"\x00image/png\x00" + bytes([picture_type]) + b"\x00" + png)


def _syncsafe(n: int) -> bytes:
    return bytes([(n >> 21) & 0x7F, (n >> 14) & 0x7F, (n >> 7) & 0x7F, n & 0x7F])


def _unsyncsafe(b: bytes) -> int:
    return (b[0] << 21) | (b[1] << 14) | (b[2] << 7) | b[3]


def build_v2(version: int, frames: list[RawFrame], padding: int = 256) -> bytes:
    """Build an ID3v2.3 or v2.4 tag."""
    body = b""
    for frame in frames:
        size = _syncsafe(len(frame.data)) if version == 4 else struct.pack(">I", len(frame.data))
        body += frame.id.encode() + size + frame.flags + frame.data
    body += b"\x00" * padding
    return b"ID3" + bytes([version, 0, 0]) + _syncsafe(len(body)) + body


def build_v1(title: str, artist: str, album: str, year: str, comment: str, track: int) -> bytes:
    """Build an ID3v1.1 footer with no genre (255)."""

    def field(value: str, size: int) -> bytes:
        return value.encode("latin-1")[:size].ljust(size, b"\x00")

    return (
        b"TAG"
        + field(title, 30)
        + field(artist, 30)
        + field(album, 30)
        + field(year, 4)
        + field(comment, 28)
        + b"\x00"
        + bytes([track, 255])
    )


def parse_mp3(path: Path) -> RawMp3:
    """Split an MP3 file into its ID3v2 frames, audio and ID3v1 footer."""
    data = path.read_bytes()
    if data[:3] != b"ID3":
        raise ValueError(f"{path.name} has no ID3v2 tag")
    version = data[3]
    tag_end = 10 + _unsyncsafe(data[6:10])
    frames: list[RawFrame] = []
    pos = 10
    while pos + 10 <= tag_end and data[pos] != 0:
        frame_id = data[pos : pos + 4].decode("latin-1")
        raw_size = data[pos + 4 : pos + 8]
        size = _unsyncsafe(raw_size) if version == 4 else struct.unpack(">I", raw_size)[0]
        flags = data[pos + 8 : pos + 10]
        frames.append(RawFrame(frame_id, data[pos + 10 : pos + 10 + size], flags))
        pos += 10 + size
    has_v1 = data[-128:-125] == b"TAG"
    audio_end = len(data) - 128 if has_v1 else len(data)
    return RawMp3(
        version=version,
        frames=frames,
        padding=tag_end - pos,
        audio=data[tag_end:audio_end],
        v1=data[-128:] if has_v1 else None,
    )
