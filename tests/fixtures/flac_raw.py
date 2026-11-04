"""Builds and parses FLAC metadata blocks byte by byte, without mutagen."""

import struct
from dataclasses import dataclass
from pathlib import Path

STREAMINFO = 0
PADDING = 1
VORBIS_COMMENT = 4
PICTURE = 6


@dataclass(frozen=True, slots=True)
class RawBlock:
    """One FLAC metadata block: its type and payload."""

    type: int
    data: bytes


@dataclass(frozen=True, slots=True)
class RawFlac:
    """A FLAC file split into its metadata blocks and audio frames."""

    blocks: list[RawBlock]
    audio: bytes

    def block(self, block_type: int) -> RawBlock:
        """The only block of a type. Fails if there are none or several."""
        (found,) = [b for b in self.blocks if b.type == block_type]
        return found


def vorbis_comment(vendor: str, comments: list[tuple[str, str]]) -> RawBlock:
    """A Vorbis comment block. Repeated keys are how FLAC stores several values."""
    data = struct.pack("<I", len(vendor.encode())) + vendor.encode()
    data += struct.pack("<I", len(comments))
    for key, value in comments:
        entry = f"{key}={value}".encode()
        data += struct.pack("<I", len(entry)) + entry
    return RawBlock(VORBIS_COMMENT, data)


def parse_vorbis_comment(block: RawBlock) -> tuple[str, list[tuple[str, str]]]:
    """The vendor string and comments of a Vorbis comment block, in order."""
    data = block.data
    (vendor_len,) = struct.unpack_from("<I", data, 0)
    pos = 4 + vendor_len
    vendor = data[4:pos].decode()
    (count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    comments: list[tuple[str, str]] = []
    for _ in range(count):
        (size,) = struct.unpack_from("<I", data, pos)
        key, _, value = data[pos + 4 : pos + 4 + size].decode().partition("=")
        comments.append((key, value))
        pos += 4 + size
    return vendor, comments


def picture(png: bytes, width: int, height: int, picture_type: int = 3) -> RawBlock:
    """A PICTURE block holding a PNG, front cover by default."""
    mime = b"image/png"
    data = struct.pack(">II", picture_type, len(mime)) + mime
    data += struct.pack(">I", 0)  # empty description
    data += struct.pack(">IIIII", width, height, 24, 0, len(png)) + png
    return RawBlock(PICTURE, data)


def parse_flac(path: Path) -> RawFlac:
    """Split a FLAC file into its metadata blocks and audio frames."""
    data = path.read_bytes()
    if data[:4] != b"fLaC":
        raise ValueError(f"{path.name} isn't a FLAC file")
    blocks: list[RawBlock] = []
    pos = 4
    while True:
        header = data[pos]
        size = int.from_bytes(data[pos + 1 : pos + 4], "big")
        blocks.append(RawBlock(header & 0x7F, data[pos + 4 : pos + 4 + size]))
        pos += 4 + size
        if header & 0x80:
            break
    return RawFlac(blocks, data[pos:])


def build_flac(blocks: list[RawBlock], audio: bytes) -> bytes:
    """Assemble a FLAC file from metadata blocks and audio frames."""
    out = b"fLaC"
    for i, block in enumerate(blocks):
        last = 0x80 if i == len(blocks) - 1 else 0
        out += bytes([last | block.type]) + len(block.data).to_bytes(3, "big") + block.data
    return out + audio
