"""Checks that the project is wired up: packages import, Qt stays out of the core, the app opens."""

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from mutagen.id3 import ID3
from pytestqt.qtbot import QtBot

from crateclean.cli import main as cli_main
from crateclean.ui.app import MainWindow

CORE_MODULES = (
    "crateclean.engine",
    "crateclean.match",
    "crateclean.apis",
    "crateclean.store",
    "crateclean.cli",
)


@pytest.mark.parametrize("module", CORE_MODULES)
def test_core_module_does_not_import_qt(module: str) -> None:
    # A fresh interpreter, so modules other tests already imported don't count.
    code = f"import sys, {module}; print(any(m.startswith('PySide6') for m in sys.modules))"
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "False"


def test_cli_runs_with_no_arguments() -> None:
    assert cli_main([]) == 0


def test_generated_mp3_has_its_id3v23_tags(fixture_copy: Callable[[str], Path]) -> None:
    tags = ID3(fixture_copy("id3v23.mp3"), translate=False)
    assert tags.version[:2] == (2, 3)
    assert str(tags["TIT2"]) == "Night Drive (Original Mix)"


def test_main_window_opens(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()
    assert window.windowTitle() == "CrateClean"
