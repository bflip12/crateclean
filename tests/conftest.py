"""Shared fixtures: the generated audio files, copied into each test's temporary folder."""

import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.fixtures.make_fixtures import make_fixtures


@pytest.fixture(scope="session")
def generated_dir() -> Path:
    """The folder of generated fixtures. Tests copy from it and never change it."""
    return make_fixtures()


@pytest.fixture
def fixture_copy(generated_dir: Path, tmp_path: Path) -> Callable[[str], Path]:
    """Copies a generated fixture, by file name, into the test's temporary folder."""

    def copy(name: str) -> Path:
        return Path(shutil.copy2(generated_dir / name, tmp_path / name))

    return copy
