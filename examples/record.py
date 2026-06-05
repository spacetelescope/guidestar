#!/usr/bin/env python3
"""
Record wireframe demo pages as animated GIFs.

This script is a thin wrapper around the guidestar-record CLI.
For direct usage install the package and run:

    guidestar-record --configs-dir examples/demos --site _site

Local usage (without installing):

    python examples/record.py [--site _site] [--out _site] [--fps 10] [--width 800]
"""

import sys
from pathlib import Path

# Allow running from the repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from guidestar.cli.record import main  # noqa: E402


def _local_main():
    """Wrapper that injects the repo-local configs-dir before delegating."""
    import argparse
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--site", default="_site")
    pre.add_argument("--out", default=None)
    pre.add_argument("--demo", default=None)
    pre.add_argument("--fps", type=int, default=10)
    pre.add_argument("--width", type=int, default=800)
    known, _ = pre.parse_known_args()

    root = Path(__file__).resolve().parent.parent
    argv = [
        "guidestar-record",
        "--configs-dir", str(root / "examples" / "demos"),
        "--site", known.site,
        "--fps", str(known.fps),
        "--width", str(known.width),
    ]
    if known.out:
        argv += ["--out", known.out]
    if known.demo:
        argv += ["--demo", known.demo]

    sys.argv = argv
    main()


if __name__ == "__main__":
    _local_main()

