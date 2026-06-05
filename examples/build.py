#!/usr/bin/env python3
"""
Build self-contained wireframe demo pages.

This script is a thin wrapper around the guidestar-build CLI.
For direct usage install the package and run:

    guidestar-build --configs-dir examples/demos --out _site

Local usage (without installing):

    python examples/build.py --out _site
"""

import sys
from pathlib import Path

# Allow running from the repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


from guidestar.cli.build import main  # noqa: E402


def _local_main():
    """Wrapper that injects the repo-local default paths before delegating."""
    import argparse
    # Parse just --out so we can rewrite argv into the CLI's expected form
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--out", default="_site")
    known, _ = pre.parse_known_args()

    root = Path(__file__).resolve().parent.parent
    sys.argv = [
        "guidestar-build",
        "--configs-dir", str(root / "examples" / "demos"),
        "--wireframes-dir", str(root / "examples" / "wireframes"),
        "--out", known.out,
    ]
    main()


if __name__ == "__main__":
    _local_main()

