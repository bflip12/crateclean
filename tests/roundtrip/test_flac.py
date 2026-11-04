"""FLAC round trips: Vorbis comments and PICTURE blocks (ADR 0005).

Files are read back with `tests.fixtures.flac_raw`, not mutagen.
"""

from collections import Counter
from collections.abc import Callable
from pathlib import Path

from mutagen.flac import FLAC, Picture

from crateclean.engine.tag_io import load_flac
from crateclean.engine.write import save_flac
from tests.fixtures import flac_raw
from tests.fixtures.flac_raw import RawFlac, parse_flac
from tests.fixtures.make_fixtures import FLAC_COMMENTS, TITLE

Fixture = Callable[[str], Path]


def _round_trip(
    path: Path, edit: Callable[[FLAC], None] = lambda tags: None
) -> tuple[RawFlac, RawFlac]:
    before = parse_flac(path)
    tags = load_flac(path)
    edit(tags)
    save_flac(tags)
    return before, parse_flac(path)


def _comments(flac: RawFlac) -> list[tuple[str, str]]:
    return flac_raw.parse_vorbis_comment(flac.block(flac_raw.VORBIS_COMMENT))[1]


def test_keeps_comments_in_order_with_repeated_keys(fixture_copy: Fixture) -> None:
    _, after = _round_trip(fixture_copy("tags.flac"))
    assert _comments(after) == FLAC_COMMENTS


def test_keeps_the_vendor_string(fixture_copy: Fixture) -> None:
    before, after = _round_trip(fixture_copy("tags.flac"))
    vendor = flac_raw.parse_vorbis_comment(after.block(flac_raw.VORBIS_COMMENT))[0]
    assert vendor == flac_raw.parse_vorbis_comment(before.block(flac_raw.VORBIS_COMMENT))[0]


def test_keeps_streaminfo_picture_and_audio_identical(fixture_copy: Fixture) -> None:
    before, after = _round_trip(fixture_copy("tags.flac"))
    assert after.block(flac_raw.STREAMINFO) == before.block(flac_raw.STREAMINFO)
    assert after.block(flac_raw.PICTURE) == before.block(flac_raw.PICTURE)
    assert after.audio == before.audio


def test_changes_only_the_edited_comment(fixture_copy: Fixture) -> None:
    def edit(tags: FLAC) -> None:
        tags["TITLE"] = ["Night Drive"]

    before, after = _round_trip(fixture_copy("tags.flac"), edit)
    removed = Counter(_comments(before)) - Counter(_comments(after))
    added = Counter(_comments(after)) - Counter(_comments(before))
    assert removed == Counter({("TITLE", TITLE): 1})
    assert added == Counter({("TITLE", "Night Drive"): 1})
    assert after.block(flac_raw.PICTURE) == before.block(flac_raw.PICTURE)
    assert after.audio == before.audio


def test_keeps_both_values_of_a_repeated_key(fixture_copy: Fixture) -> None:
    def edit(tags: FLAC) -> None:
        tags["TITLE"] = ["Night Drive"]

    _, after = _round_trip(fixture_copy("tags.flac"), edit)
    assert [value for key, value in _comments(after) if key == "ARTIST"] == [
        "Artist One",
        "Artist Two",
    ]


def test_adds_a_picture_without_touching_the_existing_one(fixture_copy: Fixture) -> None:
    new_cover = b"\x89PNG\r\n\x1a\n" + b"new cover" * 10

    def edit(tags: FLAC) -> None:
        picture = Picture()
        picture.type = 4  # back cover, so it can't be confused with the existing front cover
        picture.mime = "image/png"
        picture.width = picture.height = 10
        picture.depth = 24
        picture.data = new_cover
        tags.add_picture(picture)

    before, after = _round_trip(fixture_copy("tags.flac"), edit)
    pictures = [b for b in after.blocks if b.type == flac_raw.PICTURE]
    assert pictures[0] == before.block(flac_raw.PICTURE)
    assert pictures[1].data.endswith(new_cover)
    assert _comments(after) == _comments(before)
    assert after.audio == before.audio
