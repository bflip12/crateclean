# PyInstaller spec for the CrateClean app. Build with:
#
#     uv run pyinstaller packaging/crateclean.spec --noconfirm
#
# The app lands in dist/ (CrateClean.app on macOS, a CrateClean folder on Windows).
#
# Analysis, PYZ, EXE, COLLECT, BUNDLE and SPECPATH are provided by PyInstaller when it runs this.

import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent
APP_NAME = "CrateClean"

a = Analysis(
    [str(ROOT / "src" / "crateclean" / "ui" / "app.py")],
    pathex=[str(ROOT / "src")],
    # Qt modules the app doesn't use, kept out to shrink the download.
    excludes=["PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtWebEngineCore", "tkinter"],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        bundle_identifier="io.github.bflip12.crateclean",
        info_plist={
            "CFBundleDisplayName": APP_NAME,
            "NSHighResolutionCapable": True,
        },
    )
