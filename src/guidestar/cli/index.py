#!/usr/bin/env python3
"""
Generate a minimal index.html listing all built demo pages.

Scans the output directory for *.html files (excluding index.html itself)
and writes a simple index page that links to each demo and, if a matching
.gif exists alongside the HTML, shows it as a preview thumbnail.

Usage:
    guidestar-index --site _site
    guidestar-index --site _site --title "My Project Demos"
"""

import html
import sys
from pathlib import Path


_PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{
    font-family: system-ui, sans-serif;
    margin: 0;
    padding: 2rem;
    background: #f8f9fa;
    color: #212529;
  }}
  h1 {{
    font-size: 1.5rem;
    margin: 0 0 1.5rem;
  }}
  ul {{
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
  }}
  li a {{
    display: block;
    padding: 1rem;
    background: #fff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    text-decoration: none;
    color: inherit;
    transition: box-shadow 0.15s;
  }}
  li a:hover {{
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }}
  li a img {{
    display: block;
    width: 100%;
    border-radius: 3px;
    margin-bottom: 0.5rem;
  }}
  li a .name {{
    font-weight: 600;
    font-size: 0.95rem;
  }}
</style>
</head>
<body>
<h1>{title}</h1>
<ul>
{items}
</ul>
</body>
</html>
"""

_ITEM_WITH_GIF = """\
  <li>
    <a href="{href}">
      <img src="{gif}" alt="{name} preview">
      <span class="name">{name}</span>
    </a>
  </li>"""

_ITEM_PLAIN = """\
  <li>
    <a href="{href}">
      <span class="name">{name}</span>
    </a>
  </li>"""


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a minimal index.html listing all built demo pages."
    )
    parser.add_argument(
        "--site",
        default="_site",
        help="Directory containing built demo pages (default: _site).",
    )
    parser.add_argument(
        "--title",
        default="Wireframe Demos",
        help="Page title (default: 'Wireframe Demos').",
    )
    args = parser.parse_args(argv)

    site_dir = Path(args.site)
    if not site_dir.is_dir():
        print(f"ERROR: site directory not found: {site_dir}")
        sys.exit(1)

    demo_pages = sorted(
        p for p in site_dir.glob("*.html") if p.stem != "index"
    )

    if not demo_pages:
        print(f"No demo HTML pages found in {site_dir}")
        sys.exit(1)

    items = []
    for page in demo_pages:
        name = html.escape(page.stem)
        href = html.escape(page.name)
        gif = page.with_suffix(".gif")
        if gif.exists():
            items.append(
                _ITEM_WITH_GIF.format(href=href, gif=html.escape(gif.name), name=name)
            )
        else:
            items.append(_ITEM_PLAIN.format(href=href, name=name))

    title = html.escape(args.title)
    content = _PAGE_TEMPLATE.format(title=title, items="\n".join(items))

    out_path = site_dir / "index.html"
    out_path.write_text(content, encoding="utf-8")
    print(f"→ {out_path} ({len(demo_pages)} demo(s) listed)")


if __name__ == "__main__":
    main()
