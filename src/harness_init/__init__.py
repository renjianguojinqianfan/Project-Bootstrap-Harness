"""harness_init package."""

try:
    from importlib.metadata import version

    __version__ = version("harness-init")
except Exception:  # pragma: no cover
    __version__ = "1.1.6"
