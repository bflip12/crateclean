"""Reads the iTunes metadata atoms and audio data of an MP4 file byte by byte, without mutagen."""

import struct
from dataclasses import dataclass
from pathlib import Path

# Atoms that only hold other atoms, with the bytes to skip before their children.
_CONTAINERS = {b"moov": 0, b"udta": 0, b"meta": 4, b"ilst": 0}


@dataclass(frozen=True, slots=True)
class RawMp4:
    """The metadata items in `moov/udta/meta/ilst`, in order, and the `mdat` payload."""

    items: list[tuple[bytes, bytes]]
    audio: bytes

    def item(self, name: bytes) -> bytes:
        """The raw bytes of the only item with this atom name."""
        (found,) = [data for item_name, data in self.items if item_name == name]
        return found


def _atoms(data: bytes, start: int, end: int) -> list[tuple[bytes, int, int]]:
    """(name, payload start, payload end) for each atom between start and end."""
    found: list[tuple[bytes, int, int]] = []
    pos = start
    while pos + 8 <= end:
        size, name = struct.unpack_from(">I4s", data, pos)
        header = 8
        if size == 1:
            (size,) = struct.unpack_from(">Q", data, pos + 8)
            header = 16
        elif size == 0:
            size = end - pos
        found.append((name, pos + header, pos + size))
        pos += size
    return found


def _find(data: bytes, path: list[bytes]) -> tuple[int, int]:
    """The children's start and end of the container at `path`."""
    start, end = 0, len(data)
    for name in path:
        ((child_start, end),) = [(s, e) for n, s, e in _atoms(data, start, end) if n == name]
        start = child_start + _CONTAINERS[name]
    return start, end


def parse_mp4(path: Path) -> RawMp4:
    """Read an MP4 file's metadata items and audio payload."""
    data = path.read_bytes()
    ilst_start, ilst_end = _find(data, [b"moov", b"udta", b"meta", b"ilst"])
    items = [(name, data[s:e]) for name, s, e in _atoms(data, ilst_start, ilst_end)]
    (mdat_start, mdat_end) = next((s, e) for n, s, e in _atoms(data, 0, len(data)) if n == b"mdat")
    return RawMp4(items, data[mdat_start:mdat_end])
