#!/usr/bin/env python3
"""
Build self-contained wireframe demo pages.

For each JSON config in the configs directory, this script:
1. Reads the referenced wireframe HTML
2. Extracts the <body> content and <style> blocks
3. Inlines everything into a single self-contained page with the
   controller JS/CSS, the wireframe content, and the step config
4. Writes the output to the specified output directory

The output pages work in iframes (no fetch() calls) and can be
embedded in Confluence or any other platform.

Usage:
    guidestar-build --configs-dir guidestar-demos --out _site
    guidestar-build --configs-dir guidestar-demos --wireframes-dir path/to/wireframes --out _site
"""

import html
import json
import re
import sys
from importlib.resources import files
from pathlib import Path


def _static_dir() -> Path:
    """Return the path to the bundled guidestar static assets."""
    return Path(str(files("guidestar").joinpath("static")))


def extract_body_and_styles(wireframe_html: str) -> tuple[str, str]:
    """Extract <style> blocks and <body> content from a wireframe HTML file.

    Returns (styles_html, body_html).
    """
    styles = re.findall(r"<style[^>]*>.*?</style>", wireframe_html, re.DOTALL)
    styles_html = "\n".join(styles)

    body_match = re.search(r"<body[^>]*>(.*)</body>", wireframe_html, re.DOTALL)
    body_html = body_match.group(1).strip() if body_match else wireframe_html

    return styles_html, body_html


def build_page(demo_config: dict, wireframe_path: Path, controller_js: str, controls_css: str) -> str:
    """Build a self-contained HTML page from a demo config and wireframe."""
    wireframe_html = wireframe_path.read_text(encoding="utf-8")
    styles_html, body_html = extract_body_and_styles(wireframe_html)

    title = demo_config.get("title", "Wireframe Demo")
    height = demo_config.get("height", "100vh")

    config = {
        "steps": demo_config.get("steps", []),
        "repeat": demo_config.get("repeat", True),
        "autoStart": demo_config.get("autoStart", True),
    }
    for key in ("initSteps", "pauseOnInteraction", "initialClass", "cursor", "cursorSpeed", "viewport"):
        if demo_config.get(key) is not None:
            config[key] = demo_config[key]

    config_json = html.escape(json.dumps(config), quote=True)

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>
  body {{
    margin: 0;
    overflow: hidden;
    background: transparent;
  }}
  [data-guidestar] {{
    width: 100%;
    height: {height};
  }}
</style>
<style>
/* guidestar-controls.css (inlined) */
{controls_css}
</style>
{styles_html}
</head>
<body>
<div data-guidestar
     data-guidestar-config="{config_json}">
{body_html}
</div>
<script>
// guidestar-controller.js (inlined)
{controller_js}
</script>
</body>
</html>
"""


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        description="Build self-contained wireframe demo pages from JSON configs."
    )
    parser.add_argument(
        "--configs-dir",
        required=True,
        help="Directory containing demo JSON config files.",
    )
    parser.add_argument(
        "--wireframes-dir",
        default=None,
        help="Directory containing wireframe HTML files. "
             "Defaults to <configs-dir>/wireframes.",
    )
    parser.add_argument(
        "--out",
        default="_site",
        help="Output directory for built HTML pages (default: _site).",
    )
    args = parser.parse_args(argv)

    configs_dir = Path(args.configs_dir)
    wireframes_dir = Path(args.wireframes_dir) if args.wireframes_dir else configs_dir / "wireframes"
    out_dir = Path(args.out)

    if not configs_dir.is_dir():
        print(f"ERROR: configs directory not found: {configs_dir}")
        sys.exit(1)
    if not wireframes_dir.is_dir():
        print(f"ERROR: wireframes directory not found: {wireframes_dir}")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    static = _static_dir()
    controller_js = (static / "guidestar-controller.js").read_text(encoding="utf-8")
    controls_css = (static / "guidestar-controls.css").read_text(encoding="utf-8")

    demo_files = sorted(configs_dir.glob("*.json"))
    if not demo_files:
        print(f"No demo configs found in {configs_dir}")
        sys.exit(1)

    built = 0
    for demo_file in demo_files:
        print(f"Building {demo_file.name}...")
        demo_config = json.loads(demo_file.read_text(encoding="utf-8"))

        wireframe_name = demo_config.get("wireframe")
        if not wireframe_name:
            print(f"  SKIP: no 'wireframe' key in {demo_file.name}")
            continue

        wireframe_path = wireframes_dir / wireframe_name
        if not wireframe_path.exists():
            print(f"  ERROR: wireframe not found: {wireframe_path}")
            sys.exit(1)

        page_html = build_page(demo_config, wireframe_path, controller_js, controls_css)

        out_path = out_dir / (demo_file.stem + ".html")
        out_path.write_text(page_html, encoding="utf-8")
        print(f"  → {out_path}")
        built += 1

    print(f"\nBuilt {built} demo page(s) in {out_dir}")


if __name__ == "__main__":
    main()
