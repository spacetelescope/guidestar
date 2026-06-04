"""
guidestar: Reusable wireframe demo infrastructure for Sphinx and standalone HTML.
"""

try:
    from importlib.metadata import version
    __version__ = version("guidestar")
except Exception:
    __version__ = "unknown"


def setup(app):
    """Sphinx extension entry point."""
    from .extension import setup as _setup
    return _setup(app)
