"""Exceptions raised by the engine. Their messages are ready to show to the user."""


class EngineError(Exception):
    """Base class for errors the engine reports to the user."""


class UnsupportedTagError(EngineError):
    """A file's tags are in a format CrateClean can't write without changing it."""
