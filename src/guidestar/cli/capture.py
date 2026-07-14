#!/usr/bin/env python3
"""
guidestar-capture — Drive a Robot Framework .robot file with Playwright and
produce a static Guidestar wireframe from the captured page states.

Usage:
    guidestar-capture path/to/demo.robot [options]

Options:
    --out DIR           Output directory for wireframe HTML + JSON config
                        (default: same directory as the .robot file)
    --mode screenshot   Capture mode: screenshot (default) or dom
           dom
    --viewport INT      Browser viewport width in pixels (default: 1440,
                        can be overridden per-file via Library arguments)
    --height STR        Container height CSS value (default: 700px,
                        can be overridden per-file via Library arguments)
    --rst               Also write a Sphinx directive .rst snippet
    --standalone        Also write a self-contained demo HTML page

Requires:
    pip install 'sphinx-guidestar[capture]' && playwright install chromium

The .robot file must use the GuidestarCapture library:

    *** Settings ***
    Library    guidestar.rf.GuidestarCapture    capture_mode=screenshot

    *** Test Cases ***
    My Demo
        Open Capture    https://example.com/myapp
        Route API       **/api/search**    body_file=mock.json
        Wait For Selector    #search-input
        Capture Step    caption=The search form    delay=2500
        Fill Text       #search-input    hello world
        Click Element   button[type="submit"]
        Wait For Selector    .results
        Capture Step    caption=Search results loaded    delay=3000
        Export Demo     my-demo    out_dir=examples/wireframes
"""

import argparse
import os
import sys
from pathlib import Path


def _check_deps() -> None:
    missing = []
    try:
        import robot  # noqa: F401
    except ImportError:
        missing.append("robotframework")
    try:
        import playwright  # noqa: F401
    except ImportError:
        missing.append("playwright")
    if missing:
        pkg = " ".join(missing)
        print(
            f"ERROR: Missing dependencies: {pkg}\n"
            "Install with: pip install 'sphinx-guidestar[capture]' "
            "&& playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="guidestar-capture",
        description=(
            "Drive a Robot Framework .robot file with Playwright and capture "
            "the page states as a static Guidestar wireframe + demo config."
        ),
    )
    parser.add_argument(
        "robot_file",
        metavar="ROBOT_FILE",
        help="Path to the .robot file to execute.",
    )
    parser.add_argument(
        "--out",
        metavar="DIR",
        default=None,
        help=(
            "Output directory for wireframe and config files.  Defaults to the "
            "directory containing ROBOT_FILE if not specified here and not set "
            "via the 'Export Demo' keyword's out_dir argument."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["screenshot", "dom"],
        default=None,
        help=(
            "Capture mode.  Overrides the capture_mode Library argument in the "
            ".robot file if provided.  screenshot (default): full-viewport PNGs "
            "embedded as base64.  dom: live DOM snapshot with inlined assets."
        ),
    )
    parser.add_argument(
        "--viewport",
        type=int,
        default=None,
        help="Browser viewport width in pixels (overrides Library argument).",
    )
    parser.add_argument(
        "--height",
        default=None,
        help="Container height CSS value, e.g. 700px (overrides Library argument).",
    )
    parser.add_argument(
        "--rst",
        action="store_true",
        help="Also write a Sphinx directive .rst snippet alongside the wireframe.",
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Also write a self-contained demo HTML page with the controller inlined.",
    )

    args = parser.parse_args(argv)

    _check_deps()

    robot_file = Path(args.robot_file).resolve()
    if not robot_file.exists():
        print(f"ERROR: {robot_file} does not exist.", file=sys.stderr)
        sys.exit(1)

    # Inject CLI overrides as environment variables that the RF library reads.
    # The GuidestarCapture library checks these at Open Capture time so that
    # CLI flags take precedence over Library constructor arguments.
    env_overrides: dict[str, str] = {}
    if args.mode:
        env_overrides["GUIDESTAR_CAPTURE_MODE"] = args.mode
    if args.viewport:
        env_overrides["GUIDESTAR_CAPTURE_VIEWPORT"] = str(args.viewport)
    if args.height:
        env_overrides["GUIDESTAR_CAPTURE_HEIGHT"] = args.height
    if args.out:
        env_overrides["GUIDESTAR_CAPTURE_OUT_DIR"] = str(Path(args.out).resolve())
    if args.rst:
        env_overrides["GUIDESTAR_CAPTURE_RST"] = "1"
    if args.standalone:
        env_overrides["GUIDESTAR_CAPTURE_STANDALONE"] = "1"

    for k, v in env_overrides.items():
        os.environ[k] = v

    # Make the guidestar.rf package importable from the RF runner
    src_dir = Path(__file__).resolve().parent.parent.parent  # src/
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    import robot

    output_dir = Path(args.out).resolve() if args.out else robot_file.parent / "_capture_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"guidestar-capture: running {robot_file.name}")
    print(f"  mode:     {args.mode or '(from .robot file)'}")
    print(f"  out:      {args.out or '(from Export Demo keyword)'}")
    print()

    rc = robot.run(
        str(robot_file),
        outputdir=str(output_dir),
        log=str(output_dir / "log.html"),
        report=str(output_dir / "report.html"),
        output=str(output_dir / "output.xml"),
    )

    # Clean up env overrides
    for k in env_overrides:
        os.environ.pop(k, None)

    if rc != 0:
        print(
            f"\nguidestar-capture: Robot Framework reported {rc} failure(s).\n"
            f"See {output_dir / 'log.html'} for details.",
            file=sys.stderr,
        )
        sys.exit(rc)

    print("\nguidestar-capture: complete.")


if __name__ == "__main__":
    main()
