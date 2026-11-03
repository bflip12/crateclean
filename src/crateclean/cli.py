"""The command line for the engine, for trying the cleaning rules on a folder and for scripting.

Commands (`scan`, `preview`, `apply`) are added as the engine is built.
"""

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for `crateclean-cli`."""
    return argparse.ArgumentParser(
        prog="crateclean-cli",
        description="Clean junk out of DJ music tags without breaking your Rekordbox library.",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return its exit code.

    Args:
        argv: The arguments after the program name. `None` reads them from `sys.argv`.
    """
    build_parser().parse_args(argv)
    return 0
