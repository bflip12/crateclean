"""ID3 round trips: the cases in ADR 0005, on ID3v2.3 and v2.4 MP3s.

Files are read back with `tests.fixtures.id3_raw`, not mutagen, so a mutagen bug can't hide
itself.
"""

from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pytest
from mutagen.id3 import COMM, ID3, TIT2

from crateclean.engine.tag_io import load_id3, read_id3v1
from crateclean.engine.write import save_id3
from tests.fixtures import id3_raw
from tests.fixtures.id3_raw import RawFrame, RawMp3, parse_mp3
from tests.fixtures.make_fixtures import MAIN_COMMENT, TITLE

MP3_FIXTURES = [pytest.param("id3v23.mp3", 3, id="v2.3"), pytest.param("id3v24.mp3", 4, id="v2.4")]
BINARY_FRAMES = {"POPM", "GEOB", "PRIV", "APIC", "ZZRB"}

Decoded = tuple[object, ...]


def _split(body: bytes, encoding: int) -> list[str]:
    """Split null-separated values, dropping the empty value a trailing terminator leaves."""
    if encoding == id3_raw.UTF16:
        values: list[str] = []
        start = 0
        for i in range(0, len(body) - 1, 2):
            if body[i : i + 2] == b"\x00\x00":
                values.append(body[start:i].decode("utf-16"))
                start = i + 2
        values.append(body[start:].decode("utf-16") if body[start:] else "")
    else:
        codec = "latin-1" if encoding == id3_raw.LATIN1 else "utf-8"
        values = [part.decode(codec) for part in body.split(b"\x00")]
    return values[:-1] if len(values) > 1 and values[-1] == "" else values


def _decode(frame: RawFrame) -> Decoded:
    """A frame's meaning, independent of how its strings are terminated."""
    if frame.id in BINARY_FRAMES or not frame.id.startswith(("T", "COMM")):
        return (frame.id, frame.data)
    encoding, body = frame.data[0], frame.data[1:]
    if frame.id == "COMM":
        lang = body[:3]
        description, *text = _split(body[3:], encoding)
        return (frame.id, lang, description, tuple(text))
    if frame.id == "TXXX":
        description, *values = _split(body, encoding)
        return (frame.id, description, tuple(values))
    return (frame.id, tuple(_split(body, encoding)))


def _decoded(mp3: RawMp3) -> Counter[Decoded]:
    return Counter(_decode(frame) for frame in mp3.frames)


def _round_trip(
    path: Path, edit: Callable[[ID3], None] = lambda tags: None
) -> tuple[RawMp3, RawMp3]:
    before = parse_mp3(path)
    tags = load_id3(path)
    edit(tags)
    save_id3(tags, path, read_id3v1(path))
    return before, parse_mp3(path)


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_keeps_the_tag_version(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    before, after = _round_trip(fixture_copy(name))
    assert before.version == after.version == version


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_keeps_the_audio_identical(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    before, after = _round_trip(fixture_copy(name))
    assert after.audio == before.audio


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_keeps_every_frame_and_value(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    before, after = _round_trip(fixture_copy(name))
    assert _decoded(after) == _decoded(before)


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_keeps_null_separated_multi_values(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    _, after = _round_trip(fixture_copy(name))
    decoded = _decoded(after)
    assert decoded[("TPE1", ("Artist One", "Artist Two"))] == 1
    assert decoded[("TXXX", "MOOD", ("Dark", "Driving"))] == 1
    # A slash inside a single value isn't a separator, and isn't split.
    assert decoded[("TPE2", ("Artist One/Artist Two",))] == 1


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_keeps_binary_and_unknown_frames_byte_identical(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    before, after = _round_trip(fixture_copy(name))

    def binary(mp3: RawMp3) -> Counter[RawFrame]:
        return Counter(frame for frame in mp3.frames if frame.id in BINARY_FRAMES)

    assert binary(after) == binary(before)
    assert len(binary(before)) == len(BINARY_FRAMES)


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_text_frames_differ_only_by_a_trailing_terminator(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    # mutagen ends every text value with a terminator; ADR 0011 accepts that and nothing more.
    def without_terminator(frame: RawFrame) -> RawFrame:
        terminator = b"\x00\x00" if frame.data[0] == id3_raw.UTF16 else b"\x00"
        data = frame.data.removesuffix(terminator)
        return RawFrame(frame.id, data, frame.flags)

    before, after = _round_trip(fixture_copy(name))
    text_before = [f for f in before.frames if f.id not in BINARY_FRAMES]
    text_after = [without_terminator(f) for f in after.frames if f.id not in BINARY_FRAMES]
    assert Counter(text_after) == Counter(text_before)


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_changes_only_the_edited_frame(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    def edit(tags: ID3) -> None:
        tags.setall("TIT2", [TIT2(encoding=0, text=["Night Drive"])])

    before, after = _round_trip(fixture_copy(name), edit)
    removed = _decoded(before) - _decoded(after)
    added = _decoded(after) - _decoded(before)
    assert removed == Counter({("TIT2", (TITLE,)): 1})
    assert added == Counter({("TIT2", ("Night Drive",)): 1})


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_comm_frames_keep_descriptor_and_language(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    _, after = _round_trip(fixture_copy(name))
    comments = {d for d in _decoded(after) if d[0] == "COMM"}
    assert comments == {
        ("COMM", b"eng", "", (MAIN_COMMENT,)),
        ("COMM", b"eng", "ID3v1 Comment", (MAIN_COMMENT,)),
        ("COMM", b"deu", "Notes", ("Second comment",)),
    }


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_deletes_one_comm_without_touching_the_others(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    def edit(tags: ID3) -> None:
        tags.delall("COMM:Notes:deu")

    before, after = _round_trip(fixture_copy(name), edit)
    assert _decoded(before) - _decoded(after) == Counter(
        {("COMM", b"deu", "Notes", ("Second comment",)): 1}
    )
    assert not _decoded(after) - _decoded(before)


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_keeps_the_id3v1_footer_identical(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    before, after = _round_trip(fixture_copy(name))
    assert after.v1 == before.v1


@pytest.mark.parametrize(("name", "version"), MP3_FIXTURES)
def test_writes_an_updated_id3v1_comment(
    fixture_copy: Callable[[str], Path], name: str, version: int
) -> None:
    path = fixture_copy(name)
    footer = id3_raw.build_v1(TITLE, "Artist One", "Test Album", "2024", "Cleaned comment", 0)
    tags = load_id3(path)
    tags.setall("COMM", [COMM(encoding=0, lang="eng", desc="", text=["Cleaned comment"])])
    save_id3(tags, path, footer)
    assert parse_mp3(path).v1 == footer


def test_does_not_copy_id3v1_values_into_the_v2_tag(tmp_path: Path, generated_dir: Path) -> None:
    # A v2 tag with only a title, and a v1 footer that also has an album and comment.
    audio = parse_mp3(generated_dir / "id3v23.mp3").audio
    v1 = id3_raw.build_v1(TITLE, "", "Album only in v1", "", "Comment only in v1", 0)
    path = tmp_path / "v1-extras.mp3"
    path.write_bytes(id3_raw.build_v2(3, [id3_raw.text("TIT2", TITLE)]) + audio + v1)

    before, after = _round_trip(path)
    assert _decoded(after) == _decoded(before)
    assert after.v1 == v1


def test_has_no_id3v1_footer_when_the_file_had_none(tmp_path: Path, generated_dir: Path) -> None:
    audio = parse_mp3(generated_dir / "id3v23.mp3").audio
    path = tmp_path / "no-v1.mp3"
    path.write_bytes(id3_raw.build_v2(3, [id3_raw.text("TIT2", TITLE)]) + audio)

    _, after = _round_trip(path)
    assert after.v1 is None
    assert after.audio == audio
