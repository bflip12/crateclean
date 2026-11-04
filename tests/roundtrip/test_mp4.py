"""M4A round trips: the ©nam, ©ART, ©alb, ©cmt and covr atoms (ADR 0005).

Files are read back with `tests.fixtures.mp4_raw`, not mutagen.
"""

from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pytest
from mutagen.mp4 import MP4, MP4Cover

from crateclean.engine.tag_io import load_mp4
from crateclean.engine.write import save_mp4
from tests.fixtures.mp4_raw import RawMp4, parse_mp4

Fixture = Callable[[str], Path]
TEXT_ATOMS = ["\xa9nam", "\xa9ART", "\xa9alb", "\xa9cmt"]


def _round_trip(
    path: Path, edit: Callable[[MP4], None] = lambda tags: None
) -> tuple[RawMp4, RawMp4]:
    before = parse_mp4(path)
    tags = load_mp4(path)
    edit(tags)
    save_mp4(tags)
    return before, parse_mp4(path)


def test_keeps_every_item_byte_identical(fixture_copy: Fixture) -> None:
    before, after = _round_trip(fixture_copy("tags.m4a"))
    assert Counter(after.items) == Counter(before.items)
    assert after.audio == before.audio


@pytest.mark.parametrize("atom", TEXT_ATOMS)
def test_changes_only_the_edited_atom(fixture_copy: Fixture, atom: str) -> None:
    def edit(tags: MP4) -> None:
        tags[atom] = ["Edited"]

    before, after = _round_trip(fixture_copy("tags.m4a"), edit)
    name = atom.encode("latin-1")
    changed = {n for n, data in after.items if dict(before.items).get(n) != data}
    assert changed == {name}
    assert after.item(name).endswith(b"Edited")
    assert after.audio == before.audio


def test_adds_a_cover_without_touching_the_existing_one(fixture_copy: Fixture) -> None:
    new_cover = b"\x89PNG\r\n\x1a\n" + b"new cover" * 10

    def edit(tags: MP4) -> None:
        covers = list(tags["covr"])
        tags["covr"] = [*covers, MP4Cover(new_cover, imageformat=MP4Cover.FORMAT_PNG)]

    before, after = _round_trip(fixture_copy("tags.m4a"), edit)
    assert before.item(b"covr") in after.item(b"covr")
    assert after.item(b"covr").endswith(new_cover)
    others = Counter(item for item in after.items if item[0] != b"covr")
    assert others == Counter(item for item in before.items if item[0] != b"covr")
    assert after.audio == before.audio
