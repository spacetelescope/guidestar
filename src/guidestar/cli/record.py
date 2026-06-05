#!/usr/bin/env python3
"""
Record wireframe demo pages as animated GIFs.

For each built HTML demo page, this script:
1. Opens it in headless Chromium via Playwright
2. Captures screenshots at regular intervals for one full cycle
3. Assembles the frames into an animated GIF using Pillow

Usage:
    guidestar-record --configs-dir guidestar-demos --site _site
    guidestar-record --configs-dir guidestar-demos --site _site --out gifs/
    guidestar-record --configs-dir guidestar-demos --site _site --demo mast-hst
    guidestar-record --configs-dir guidestar-demos --site _site --fps 10 --width 800

Requires: playwright, Pillow
    pip install "sphinx-guidestar[record]"
    playwright install chromium
"""

import json
import re
import sys
import io
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(
        "ERROR: playwright is required. "
        "Install with: pip install 'sphinx-guidestar[record]' && playwright install chromium"
    )
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print(
        "ERROR: Pillow is required. "
        "Install with: pip install 'sphinx-guidestar[record]'"
    )
    sys.exit(1)


def parse_step_delay(step) -> int:
    """Extract the delay (ms) from a step string or object."""
    if isinstance(step, dict):
        return step.get("delay", 2000)
    m = re.search(r"@(\d+)!?:", str(step))
    if m:
        return int(m.group(1))
    m = re.search(r"@(\d+)$", str(step))
    if m:
        return int(m.group(1))
    return 2000


def total_duration_ms(steps: list) -> int:
    """Calculate total duration of one demo cycle in milliseconds."""
    return sum(parse_step_delay(s) for s in steps)


def record_demo(
    html_path: Path,
    output_path: Path,
    config: dict,
    fps: int = 10,
    width: int = 800,
) -> None:
    """Record a single demo page as an animated GIF."""
    steps = config.get("steps", [])
    duration_ms = total_duration_ms(steps)

    total_ms = duration_ms + 1500  # 1s init + 0.5s tail
    interval_ms = 1000 // fps

    height_str = config.get("height", "420px")
    height = int(re.sub(r"[^\d]", "", height_str)) if re.search(r"\d", height_str) else 420

    print(f"  Duration: {duration_ms}ms, capturing {total_ms // interval_ms} frames at {fps}fps")

    frames = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})

        page.goto(f"file://{html_path.resolve()}", wait_until="domcontentloaded")
        page.add_style_tag(content=".gs-controls-host { display: none !important; }")
        page.wait_for_timeout(500)

        elapsed = 0
        while elapsed < total_ms:
            screenshot = page.screenshot(type="png")
            img = Image.open(io.BytesIO(screenshot)).convert("RGBA")
            frames.append(img)
            page.wait_for_timeout(interval_ms)
            elapsed += interval_ms

        browser.close()

    if not frames:
        print("  WARNING: No frames captured")
        return

    gif_frames = [
        frame.convert("P", palette=Image.ADAPTIVE, colors=256) for frame in frames
    ]

    gif_frames[0].save(
        output_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=interval_ms,
        loop=0,
        optimize=True,
    )

    size_kb = output_path.stat().st_size / 1024
    print(f"  → {output_path} ({size_kb:.0f} KB, {len(gif_frames)} frames)")


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        description="Record wireframe demo pages as animated GIFs."
    )
    parser.add_argument(
        "--configs-dir",
        required=True,
        help="Directory containing demo JSON config files (to read step durations).",
    )
    parser.add_argument(
        "--site",
        default="_site",
        help="Directory containing built HTML demo pages (default: _site).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output directory for GIFs (default: same as --site).",
    )
    parser.add_argument(
        "--demo",
        default=None,
        help="Record only this demo by stem name (e.g. 'mast-hst').",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=10,
        help="Frames per second (default: 10).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Viewport width in pixels (default: 800).",
    )
    args = parser.parse_args(argv)

    configs_dir = Path(args.configs_dir)
    site_dir = Path(args.site)
    out_dir = Path(args.out) if args.out else site_dir

    if not configs_dir.is_dir():
        print(f"ERROR: configs directory not found: {configs_dir}")
        sys.exit(1)
    if not site_dir.exists():
        print(f"ERROR: site directory not found: {site_dir}")
        print("Run 'guidestar-build' first.")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    demo_files = sorted(configs_dir.glob("*.json"))
    if args.demo:
        demo_files = [f for f in demo_files if f.stem == args.demo]
        if not demo_files:
            print(f"ERROR: no config found for demo '{args.demo}' in {configs_dir}")
            sys.exit(1)

    if not demo_files:
        print(f"No demo configs found in {configs_dir}")
        sys.exit(1)

    recorded = 0
    for demo_file in demo_files:
        stem = demo_file.stem
        html_path = site_dir / f"{stem}.html"

        if not html_path.exists():
            print(f"Skipping {stem}: {html_path} not found")
            continue

        print(f"Recording {stem}...")
        config = json.loads(demo_file.read_text(encoding="utf-8"))
        record_demo(html_path, out_dir / f"{stem}.gif", config, fps=args.fps, width=args.width)
        recorded += 1

    print(f"\nRecorded {recorded} GIF(s) in {out_dir}")


if __name__ == "__main__":
    main()
