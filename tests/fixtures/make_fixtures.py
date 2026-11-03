"""Generates the audio fixtures in `tests/fixtures/generated/` from silence, using ffmpeg.

`conftest.py` calls this before the tests run, so there's usually no need to run it by hand. To
rebuild the fixtures from scratch:

    uv run python -m tests.fixtures.make_fixtures --force

Tags are written by ffmpeg, never by mutagen, so the fixtures don't depend on the code under test.
"""

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

GENERATED_DIR = Path(__file__).parent / "generated"


@dataclass(frozen=True, slots=True)
class Fixture:
    """One generated audio file: its name, ffmpeg encoder options and tags."""

    name: str
    codec_args: tuple[str, ...]
    tags: dict[str, str]


FIXTURES = (
    Fixture(
        name="id3v23.mp3",
        codec_args=("-c:a", "libmp3lame", "-b:a", "128k", "-id3v2_version", "3"),
        tags={"title": "Silence", "artist": "Test Artist", "album": "Test Album"},
    ),
)


def _generate(fixture: Fixture, path: Path) -> None:
    metadata = [
        arg for key, value in fixture.tags.items() for arg in ("-metadata", f"{key}={value}")
    ]
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            "1",
            *fixture.codec_args,
            *metadata,
            str(path),
        ],
        check=True,
    )


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
    for fixture in FIXTURES:
        path = GENERATED_DIR / fixture.name
        if force or not path.exists():
            _generate(fixture, path)
    return GENERATED_DIR


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the audio fixtures for the tests.")
    parser.add_argument("--force", action="store_true", help="regenerate every fixture")
    print(make_fixtures(force=parser.parse_args().force))
