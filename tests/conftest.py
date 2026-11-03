"""Shared fixtures: the generated audio files, copied into each test's temporary folder."""

import shutil
from pathlib import Path

import pytest

from tests.fixtures.make_fixtures import make_fixtures


@pytest.fixture(scope="session")
def generated_dir() -> Path:
    """The folder of generated fixtures. Tests copy from it and never change it."""
    return make_fixtures()


@pytest.fixture
def id3v23_mp3(generated_dir: Path, tmp_path: Path) -> Path:
    """A copy of the ID3v2.3 MP3 fixture in the test's temporary folder."""
    return Path(shutil.copy2(generated_dir / "id3v23.mp3", tmp_path))
