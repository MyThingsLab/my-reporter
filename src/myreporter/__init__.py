from importlib.metadata import version

from myreporter.digest import Digest, Window, build_digest, load_entries, render_markdown
from myreporter.reporter import Reporter

__version__ = version("my-reporter")

__all__ = [
    "Digest",
    "Reporter",
    "Window",
    "build_digest",
    "load_entries",
    "render_markdown",
]
