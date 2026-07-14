"""
Robot Framework keyword library for capturing Guidestar demos from live pages.

This library drives a real Chromium browser via Playwright, intercepts API
calls with mock responses via page.route(), captures the page at each marked
step (as a screenshot or a cleaned DOM snapshot), and writes a static
wireframe HTML file plus a Guidestar JSON demo config.

The generated wireframe uses only existing Guidestar actions (add-class,
remove-class on a root element) — no controller changes required.

Capture modes
-------------
screenshot (default)
    Each Capture Step saves a full-viewport PNG (base64-encoded).  The
    wireframe shows screenshots in a CSS-toggle slideshow.  Always works
    regardless of origin, SPA complexity, or external stylesheets.
    Limitation: Guidestar cursor targets the root container, not individual
    UI elements within the screenshot.

dom
    Each Capture Step serialises the live DOM via page.content().  External
    stylesheets are fetched and inlined; external images are base64-encoded;
    <script> tags are stripped.  The wireframe preserves the real DOM so
    Guidestar can target individual elements with CSS selectors.
    Limitation: Captures are merged as stacked divs in one file — CSS from
    each captured state is namespaced under a data attribute to prevent
    conflicts.  Fonts and dynamic styles may be incomplete for external sites.
"""

from __future__ import annotations

import base64
import json
import re
import textwrap
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    from playwright.sync_api import sync_playwright, Route, Request
except ImportError:  # pragma: no cover
    sync_playwright = None  # type: ignore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _b64_png(data: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(data).decode()


def _int_px(value: str, default: int = 700) -> int:
    """Extract integer from a CSS px value like '700px'."""
    m = re.search(r"\d+", str(value))
    return int(m.group()) if m else default


def _inline_stylesheets(html: str, page_url: str, page) -> str:
    """Replace <link rel="stylesheet"> tags with inline <style> blocks."""
    def replace_link(m: re.Match) -> str:
        tag = m.group(0)
        href_m = re.search(r'href=["\']([^"\']+)["\']', tag)
        if not href_m:
            return tag
        href = href_m.group(1)
        abs_url = urljoin(page_url, href)
        try:
            css = page.evaluate(
                """async (url) => {
                    const r = await fetch(url);
                    if (!r.ok) return null;
                    return await r.text();
                }""",
                abs_url,
            )
            if css:
                return f"<style>/* inlined: {href} */\n{css}\n</style>"
        except Exception:
            pass
        return tag  # leave unchanged if fetch fails

    return re.sub(
        r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>',
        replace_link,
        html,
        flags=re.IGNORECASE,
    )


def _inline_images(html: str, page_url: str, page) -> str:
    """Convert <img src="..."> external URLs to base64 data URIs."""
    def replace_img(m: re.Match) -> str:
        full = m.group(0)
        src_m = re.search(r'src=["\']([^"\']+)["\']', full)
        if not src_m:
            return full
        src = src_m.group(1)
        if src.startswith("data:"):
            return full
        abs_url = urljoin(page_url, src)
        try:
            result = page.evaluate(
                """async (url) => {
                    const r = await fetch(url);
                    if (!r.ok) return null;
                    const buf = await r.arrayBuffer();
                    const ct = r.headers.get('content-type') || 'image/png';
                    const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
                    return `data:${ct};base64,${b64}`;
                }""",
                abs_url,
            )
            if result:
                new_src = result
                return full.replace(src_m.group(0), f'src="{new_src}"')
        except Exception:
            pass
        return full

    return re.sub(r'<img\b[^>]*>', replace_img, html, flags=re.IGNORECASE)


def _strip_scripts(html: str) -> str:
    """Remove <script> tags (inline and external)."""
    return re.sub(r'<script\b[^>]*>.*?</script>', '', html,
                  flags=re.DOTALL | re.IGNORECASE)


def _namespace_css(css_text: str, scope: str) -> str:
    """Prefix every CSS rule selector with a scoping data attribute selector.

    Handles nested @media / @supports blocks recursively so that responsive
    rules inside @media are correctly namespaced.

    html / body / :root selectors are remapped to the scope root element.
    @keyframes, @font-face, @import, and @charset blocks are passed through
    unchanged.
    """
    scope_sel = f'[data-gs-capture="{scope}"]'

    def namespace_selector(sel: str) -> str:
        sel = sel.strip()
        if not sel:
            return sel
        # Remap html/body/:root to scope root
        sel = re.sub(r'(?<![a-zA-Z-])\bhtml\b', scope_sel, sel)
        sel = re.sub(r'(?<![a-zA-Z-])\bbody\b', scope_sel, sel)
        sel = re.sub(r':root\b', scope_sel, sel)
        if sel.startswith(scope_sel) or sel.startswith('@'):
            return sel
        return f"{scope_sel} {sel}"

    def process_block(text: str) -> str:
        """Parse and namespace one CSS block (not including its outer braces)."""
        result: list[str] = []
        i = 0
        n = len(text)
        while i < n:
            # Advance past whitespace
            while i < n and text[i] in ' \t\n\r':
                i += 1
            if i >= n:
                break

            # Find next opening brace
            brace = text.find('{', i)
            if brace == -1:
                # Trailing text with no block (e.g. stray comment)
                result.append(text[i:])
                break

            selector = text[i:brace].strip()

            # Strip inline comments (/* ... */) before classifying the rule
            # type so that comments before an @media keyword don't prevent it
            # from being recognised.
            selector_clean = re.sub(r'/\*.*?\*/', '', selector, flags=re.DOTALL).strip()

            # Find the matching closing brace using depth tracking
            depth = 1
            j = brace + 1
            while j < n and depth > 0:
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                j += 1
            body = text[brace + 1:j - 1]

            # Skip to next rule
            i = j

            # ── Categorise and emit ──────────────────────────────────
            if re.match(r'@(media|supports|layer)\b', selector_clean, re.IGNORECASE):
                # Recurse into the block body so inner selectors get scoped
                inner = process_block(body)
                result.append(f"{selector_clean} {{\n{inner}\n}}")
            elif re.match(
                r'@(keyframes|font-face|import|charset|namespace)\b',
                selector_clean, re.IGNORECASE
            ):
                # Pass through unchanged
                result.append(f"{selector_clean} {{\n{body}\n}}")
            else:
                # Regular rule: namespace each comma-separated selector
                # Use selector_clean for namespacing (comments stripped)
                new_sels = [namespace_selector(s) for s in selector_clean.split(',')]
                new_sel = ', '.join(s for s in new_sels if s)
                if new_sel:
                    result.append(f"{new_sel} {{\n{body}\n}}")

        return '\n'.join(result)

    return process_block(css_text)


# ---------------------------------------------------------------------------
# Wireframe builders
# ---------------------------------------------------------------------------

def _build_screenshot_wireframe(captures: list[dict], viewport_width: int) -> str:
    """Build a CSS-toggle screenshot slideshow wireframe HTML."""
    n = len(captures)

    # Slide divs
    slides_html = "\n  ".join(
        f'<div class="gs-slide" data-slide="{i}">\n'
        f'    <img src="{c["data"]}" alt="Step {i}" '
        f'style="width:100%;display:block;vertical-align:top">\n  </div>'
        for i, c in enumerate(captures)
    )

    # CSS: one rule per slide
    css_rules = "\n  ".join(
        f"#gs-capture-root.gs-slide-active-{i} [data-slide=\"{i}\"] {{ display: block; }}"
        for i in range(n)
    )

    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <!-- Generated by guidestar-capture (screenshot mode) -->
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <style>
          /* Guidestar capture: screenshot slideshow */
          html, body {{ margin: 0; padding: 0; }}
          #gs-capture-root {{ position: relative; overflow: hidden; }}
          #gs-capture-root .gs-slide {{ display: none; }}
          {css_rules}
        </style>
        </head>
        <body>
        <div id="gs-capture-root" class="gs-slide-active-0">
          {slides_html}
        </div>
        </body>
        </html>
    """)


def _build_dom_wireframe(captures: list[dict], viewport_width: int) -> str:
    """Build a namespaced multi-state DOM wireframe HTML.

    Each capture's cleaned DOM is wrapped in a div with a data-gs-capture
    attribute.  CSS from each capture is namespaced under that attribute so
    rules from different states don't collide.  Only the active state's
    wrapper is visible; Guidestar toggles visibility via add-class/remove-class
    on the outer container.
    """
    n = len(captures)

    # Build one wrapper div per capture
    state_divs = []
    scoped_styles = []

    for i, c in enumerate(captures):
        dom = c["data"]  # already cleaned HTML string

        # Extract <style> blocks
        styles = re.findall(r'<style[^>]*>(.*?)</style>', dom, re.DOTALL | re.IGNORECASE)
        css_combined = "\n".join(styles)
        namespaced_css = _namespace_css(css_combined, str(i))
        scoped_styles.append(f"/* State {i}: {c.get('caption', '')} */\n{namespaced_css}")

        # Strip style tags from dom body; extract body content
        dom_no_style = re.sub(r'<style[^>]*>.*?</style>', '', dom,
                               flags=re.DOTALL | re.IGNORECASE)
        body_m = re.search(r'<body[^>]*>(.*)</body>', dom_no_style, re.DOTALL | re.IGNORECASE)
        body_html = body_m.group(1).strip() if body_m else dom_no_style

        state_divs.append(
            f'<div class="gs-dom-state" data-gs-capture="{i}" '
            f'style="display:none" data-caption="{c.get("caption", "")}">\n'
            f'{body_html}\n</div>'
        )

    # Visibility CSS
    vis_css = "\n  ".join(
        f"#gs-capture-root.gs-slide-active-{i} [data-gs-capture=\"{i}\"] {{ display: block !important; }}"
        for i in range(n)
    )

    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <!-- Generated by guidestar-capture (dom mode) -->
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <style>
          /* Guidestar capture: DOM state switcher */
          html, body {{ margin: 0; padding: 0; }}
          #gs-capture-root {{ position: relative; overflow: hidden; }}
          {vis_css}
        </style>
        <style>
          /* Namespaced per-state styles */
          {chr(10).join(scoped_styles)}
        </style>
        </head>
        <body>
        <div id="gs-capture-root" class="gs-slide-active-0">
        {''.join(state_divs)}
        </div>
        </body>
        </html>
    """)


def _build_demo_config(
    captures: list[dict],
    wireframe_name: str,
    height: str,
    viewport: Optional[int],
) -> dict:
    """Build a Guidestar JSON demo config for the captured steps.

    When viewport is None the config omits the field entirely, leaving
    the wireframe in responsive mode (no scaling).
    """
    steps = []
    for i in range(1, len(captures)):
        prev = i - 1
        step: dict = {
            "actions": [
                {"target": "#gs-capture-root", "action": "remove-class",
                 "value": f"gs-slide-active-{prev}"},
                {"target": "#gs-capture-root", "action": "add-class",
                 "value": f"gs-slide-active-{i}"},
            ],
            "delay": captures[i].get("delay", 2000),
        }
        cap = captures[i].get("caption", "")
        if cap:
            step["caption"] = cap
        steps.append(step)

    cfg: dict = {
        "wireframe": f"{wireframe_name}.html",
        "title": wireframe_name.replace("-", " ").replace("_", " ").title(),
        "height": height,
        "repeat": True,
        "steps": steps,
    }
    if viewport is not None:
        cfg["viewport"] = viewport
    return cfg


def _build_rst_snippet(wireframe_name: str, config: dict) -> str:
    """Generate a Sphinx guidestar-demo directive snippet."""
    steps_json = json.dumps(config["steps"])
    lines = [
        f".. guidestar-demo:: _static/{wireframe_name}.html",
        f"   :height: {config['height']}",
    ]
    if config.get("viewport"):
        lines.append(f"   :viewport: {config['viewport']}")
    lines.append(f"   :steps-json: {steps_json}")
    lines.append("   :repeat: true")
    return "\n".join(lines) + "\n"


def _build_standalone_html(
    wireframe_html: str,
    config: dict,
    wireframe_name: str,
    controller_js: str,
    controls_css: str,
) -> str:
    """Build a standalone demo HTML page (controller + wireframe + config inlined)."""
    import html as html_module

    styles_all = re.findall(r'<style[^>]*>.*?</style>', wireframe_html, re.DOTALL)
    styles_html = "\n".join(styles_all)
    body_m = re.search(r'<body[^>]*>(.*)</body>', wireframe_html, re.DOTALL)
    body_html = body_m.group(1).strip() if body_m else wireframe_html

    # Remove viewport/height from config; those come from the outer shell
    inner_cfg = {k: v for k, v in config.items() if k not in ("wireframe", "title")}
    config_json = html_module.escape(json.dumps(inner_cfg), quote=True)
    height = config.get("height", "700px")
    title = html_module.escape(config.get("title", wireframe_name))

    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
          body {{ margin: 0; padding: 0; background: transparent; }}
          [data-guidestar] {{ width: 100%; height: {height}; }}
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
        /* guidestar-controller.js (inlined) */
        {controller_js}
        </script>
        </body>
        </html>
    """)


# ---------------------------------------------------------------------------
# Main library class
# ---------------------------------------------------------------------------

class GuidestarCapture:
    """Robot Framework keyword library for capturing Guidestar wireframe demos.

    Arguments:
        capture_mode: ``screenshot`` (default) or ``dom``.
        viewport: Browser viewport width in pixels (default 1440).
        height: Guidestar container height CSS value (default ``"700px"``).
    """

    ROBOT_LIBRARY_SCOPE = "SUITE"
    ROBOT_LIBRARY_VERSION = "1.0"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"

    def __init__(
        self,
        capture_mode: str = "screenshot",
        viewport: int = 1440,
        height: str = "700px",
    ):
        if sync_playwright is None:
            raise RuntimeError(
                "playwright is required. "
                "Install with: pip install 'sphinx-guidestar[capture]' "
                "&& playwright install chromium"
            )
        if capture_mode not in ("screenshot", "dom"):
            raise ValueError(f"capture_mode must be 'screenshot' or 'dom', got {capture_mode!r}")

        self._mode = capture_mode
        self._viewport_width = int(viewport)
        self._height = str(height)
        self._captures: list[dict] = []
        self._routes: list[dict] = []
        self._pw = None
        self._browser = None
        self._context = None
        self._page = None
        self._page_url: str = ""

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def open_capture(
        self,
        url: str,
        viewport: Optional[int] = None,
        height: Optional[str] = None,
        wait_until: str = "networkidle",
    ) -> None:
        """Open a browser and navigate to *url*.

        Arguments:
        - ``url``        — the URL to capture (any origin).
        - ``viewport``   — override viewport width (pixels).
        - ``height``     — override container height (CSS value).
        - ``wait_until`` — Playwright wait condition (default ``networkidle``).

        Example::

            Open Capture    https://mast.stsci.edu/search/ui/#/jwst
            Open Capture    https://example.com    viewport=1280    height=600px
        """
        if viewport is not None:
            self._viewport_width = int(viewport)
        if height is not None:
            self._height = str(height)

        vp_height = _int_px(self._height, 700)
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()
        self._context = self._browser.new_context(
            viewport={"width": self._viewport_width, "height": vp_height},
        )
        self._page = self._context.new_page()

        # Re-apply any routes registered before Open Capture
        for r in self._routes:
            self._register_route(r)

        self._page.goto(url, wait_until=wait_until)
        self._page_url = url
        print(f"  [capture] Opened {url} at {self._viewport_width}×{vp_height}")

    def close_capture(self) -> None:
        """Close the browser and clean up Playwright resources.

        Called automatically by ``Export Demo`` if not already called.

        Example::

            Close Capture
        """
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._pw:
            self._pw.stop()
            self._pw = None
        self._page = None
        self._context = None

    # ── Network interception ─────────────────────────────────────────────────

    def route_api(
        self,
        url_pattern: str,
        status: int = 200,
        body: Optional[str] = None,
        body_file: Optional[str] = None,
        content_type: str = "application/json",
    ) -> None:
        """Intercept requests matching *url_pattern* and return mock data.

        The pattern uses Playwright glob syntax (``**`` for any path segment).
        Provide either ``body`` (inline JSON string) or ``body_file`` (path to
        a JSON file).

        Arguments:
        - ``url_pattern``  — Playwright URL glob, e.g. ``**/api/search**``.
        - ``status``       — HTTP status code (default 200).
        - ``body``         — Inline response body string.
        - ``body_file``    — Path to a file whose contents are the response body.
        - ``content_type`` — Response Content-Type (default ``application/json``).

        Example::

            Route API    **/api/v0.1/missions/search**    body_file=${MOCK_FILE}
            Route API    **/api/config**    body={"version": "1.0"}    status=200
        """
        route_cfg = {
            "url_pattern": url_pattern,
            "status": int(status),
            "body": body,
            "body_file": body_file,
            "content_type": content_type,
        }
        self._routes.append(route_cfg)
        if self._page:
            self._register_route(route_cfg)
        print(f"  [capture] Route registered: {url_pattern}")

    def _register_route(self, cfg: dict) -> None:
        """Attach a page.route() handler from a route config dict."""
        body_text = cfg["body"]
        if cfg["body_file"]:
            body_text = Path(cfg["body_file"]).read_text(encoding="utf-8")
        if body_text is None:
            body_text = ""

        status = cfg["status"]
        content_type = cfg["content_type"]

        def handler(route: "Route") -> None:
            route.fulfill(
                status=status,
                content_type=content_type,
                body=body_text,
            )

        self._page.route(cfg["url_pattern"], handler)

    # ── Page interactions ────────────────────────────────────────────────────

    def fill_text(self, selector: str, value: str) -> None:
        """Fill a form field identified by *selector*.

        Example::

            Fill Text    input[placeholder*="Target"]    NGC 1300
        """
        self._require_page()
        self._page.fill(selector, value)

    def click_element(self, selector: str) -> None:
        """Click the element identified by *selector*.

        Example::

            Click Element    button[type="submit"]
        """
        self._require_page()
        self._page.click(selector)

    def wait_for_selector(
        self, selector: str, timeout: int = 10000, state: str = "visible"
    ) -> None:
        """Wait until *selector* is in the given *state* (default ``visible``).

        Arguments:
        - ``selector`` — CSS selector.
        - ``timeout``  — milliseconds (default 10000).
        - ``state``    — ``attached``, ``detached``, ``visible``, or ``hidden``.

        Example::

            Wait For Selector    .results-table
            Wait For Selector    #loading-spinner    state=detached
        """
        self._require_page()
        self._page.wait_for_selector(selector, timeout=int(timeout), state=state)

    def scroll_into_view(self, selector: str) -> None:
        """Scroll *selector* into the viewport.

        Example::

            Scroll Into View    .results-table tbody tr:last-child
        """
        self._require_page()
        el = self._page.query_selector(selector)
        if el:
            el.scroll_into_view_if_needed()
        else:
            self._page.evaluate(
                f"document.querySelector('{selector}')?.scrollIntoView({{block:'center'}})"
            )

    def wait_for_timeout(self, ms: int) -> None:
        """Wait for *ms* milliseconds (useful between interactions).

        Example::

            Wait For Timeout    500
        """
        self._require_page()
        self._page.wait_for_timeout(int(ms))

    def evaluate(self, expression: str) -> object:
        """Evaluate a JavaScript *expression* in the page context and return result.

        Example::

            ${count}=    Evaluate    document.querySelectorAll('.row').length
        """
        self._require_page()
        return self._page.evaluate(expression)

    # ── Step capture ─────────────────────────────────────────────────────────

    def capture_step(self, caption: str = "", delay: int = 2000) -> None:
        """Capture the current page state as a demo step.

        In ``screenshot`` mode a full-viewport PNG is taken and base64-encoded.
        In ``dom`` mode the live DOM is serialised, external stylesheets are
        inlined, external images are converted to data URIs, and scripts are
        stripped.

        Arguments:
        - ``caption`` — caption text shown in the Guidestar demo overlay.
        - ``delay``   — milliseconds this step stays visible during playback.

        Example::

            Capture Step    caption=The search form is ready    delay=2500
        """
        self._require_page()
        n = len(self._captures)
        print(f"  [capture] Step {n}: '{caption}' ({self._mode} mode)")

        if self._mode == "screenshot":
            png_bytes = self._page.screenshot(full_page=False)
            data = _b64_png(png_bytes)
        else:
            # DOM mode: full document HTML with external resources inlined
            html_raw = self._page.content()
            html_raw = _inline_stylesheets(html_raw, self._page_url, self._page)
            html_raw = _inline_images(html_raw, self._page_url, self._page)
            html_raw = _strip_scripts(html_raw)
            data = html_raw

        self._captures.append({
            "caption": str(caption),
            "delay": int(delay),
            "data": data,
        })

    # ── Export ───────────────────────────────────────────────────────────────

    def export_demo(
        self,
        name: str,
        out_dir: str = ".",
        rst: bool = False,
        standalone: bool = False,
    ) -> None:
        """Write wireframe HTML and JSON demo config to *out_dir*.

        Filenames produced:
        - ``{name}.html``        — wireframe HTML (screenshot or DOM mode)
        - ``{name}.json``        — Guidestar JSON config (for ``guidestar-build``)
        - ``{name}.rst``         — Sphinx directive snippet  (if ``rst=True``)
        - ``{name}-standalone.html`` — self-contained demo  (if ``standalone=True``)

        Arguments:
        - ``name``       — base name for output files (no extension).
        - ``out_dir``    — output directory (created if absent).
        - ``rst``        — also write a Sphinx directive ``.rst`` snippet.
        - ``standalone`` — also write a self-contained demo HTML page.

        Example::

            Export Demo    mast-jwst-search    out_dir=examples/wireframes
            Export Demo    my-demo    out_dir=/tmp/out    rst=True    standalone=True
        """
        if not self._captures:
            raise RuntimeError(
                "No steps captured. Call Capture Step at least once before Export Demo."
            )

        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)

        # Close browser if still open
        self.close_capture()

        # Build wireframe HTML
        if self._mode == "screenshot":
            wireframe_html = _build_screenshot_wireframe(
                self._captures, self._viewport_width
            )
        else:
            wireframe_html = _build_dom_wireframe(
                self._captures, self._viewport_width
            )

        # Build demo config.
        # In DOM mode omit the viewport so the wireframe reflows responsively
        # instead of being scaled.  The browser viewport used during capture
        # (self._viewport_width) is separate from the Guidestar config field.
        config_viewport = None if self._mode == "dom" else self._viewport_width
        config = _build_demo_config(
            self._captures, name, self._height, config_viewport
        )

        # Write wireframe
        wf_path = out / f"{name}.html"
        wf_path.write_text(wireframe_html, encoding="utf-8")
        print(f"  [capture] Wrote wireframe: {wf_path}")

        # Write JSON config
        cfg_path = out / f"{name}.json"
        cfg_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        print(f"  [capture] Wrote config:    {cfg_path}")

        # Optional RST snippet
        if rst:
            rst_text = _build_rst_snippet(name, config)
            rst_path = out / f"{name}.rst"
            rst_path.write_text(rst_text, encoding="utf-8")
            print(f"  [capture] Wrote RST:       {rst_path}")

        # Optional standalone HTML
        if standalone:
            try:
                from importlib.resources import files
                static_dir = Path(str(files("guidestar").joinpath("static")))
                controller_js = (static_dir / "guidestar-controller.js").read_text()
                controls_css = (static_dir / "guidestar-controls.css").read_text()
            except Exception:
                print("  [capture] WARNING: Could not inline guidestar assets for standalone.")
                controller_js = "// guidestar-controller.js not found"
                controls_css = "/* guidestar-controls.css not found */"

            sa_html = _build_standalone_html(
                wireframe_html, config, name, controller_js, controls_css
            )
            sa_path = out / f"{name}-standalone.html"
            sa_path.write_text(sa_html, encoding="utf-8")
            print(f"  [capture] Wrote standalone: {sa_path}")

        print(f"  [capture] Done. {len(self._captures)} step(s) captured.")

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _require_page(self) -> None:
        if self._page is None:
            raise RuntimeError(
                "No browser page is open. Call 'Open Capture' first."
            )
