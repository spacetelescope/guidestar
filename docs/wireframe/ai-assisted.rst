AI Assisted
===========

Wireframes that faithfully represent a real UI are time-consuming to write
from scratch.  An AI coding agent can dramatically speed up the process by
reading source code or rendering a live page and then producing a
self-contained HTML wireframe that matches the layout, styling, and key
interactive states of the original.

The prompts below are intended for use with a capable agentic coding
assistant (e.g. GitHub Copilot agent mode, Claude Code, or similar).  Each
prompt asks the agent to produce a file that satisfies the
:doc:`structural requirements <manual>` described in the Manual section —
in particular: a single ``<style>`` block, no ``<script>`` tags, IDs on
every interactive element, and no external resource references.


Worked example — MAST HST Search
----------------------------------

The wireframe at
`examples/wireframes/mast-hst.html <../../examples/wireframes/mast-hst.html>`_
was produced by applying the "From a live web URL" prompt below to
`https://mast.stsci.edu/search/ui/#/hst/ <https://mast.stsci.edu/search/ui/#/hst/>`_.
The resulting file captures both the search-form state and the results-table
state as pure-CSS class variants (``#mast-app.results-open``) with no
JavaScript.  The built demo page is at
`_site/mast-hst.html <../../_site/mast-hst.html>`_.

.. guidestar-demo:: _static/mast-hst.html
   :steps: #input-objects@1800:type-text=M31|Enter a target name, #toggle-dtype-all@800:remove-class=checked, #toggle-dtype-spectrum@800:add-class=checked|Filter to spectra only, #mast-app@200:add-class=banner-closed, #btn-search@1200:click|Click SEARCH, #mast-app@600:add-class=results-open|Results table appears, pause@2000, #row-3@1200:add-class=highlighted|Inspect a dataset, pause@1500, #row-3@400:remove-class=highlighted, #btn-edit-search@1200:click|Return to search form, #mast-app@400:remove-class=results-open, pause@1500
   :height: 540px
   :viewport: 1440
   :repeat: true


From a Vue / JavaScript source repository
------------------------------------------

Use this prompt when the target application lives in a local or remote
repository built with Vue (or a similar component-based framework).  Adjust
the repository path and the list of components to focus on as needed.

.. code-block:: text

   You are helping me build a guidestar wireframe — a self-contained HTML
   mockup used to animate a UI demo in documentation.

   Please prompt for the location of the repository, explore the files, and
   produce a single file called wireframe.html that represents the main
   application shell.

   Requirements for the wireframe:
   - One self-contained HTML file: all CSS in a <style> block in <head>,
     no external stylesheets, no <script> tags, no external fonts or images.
   - Reproduce the overall layout: top bar / toolbar, sidebar or panel
     structure, main content area, status bar — whatever the app uses.
   - Reproduce the visual style: colours, typography scale, border radii,
     spacing, and iconography (use unicode characters or simple SVG inline
     for icons rather than icon font classes).
   - Give every interactive element (buttons, inputs, selects, tabs,
     toggleable panels) a unique id attribute so that guidestar step
     selectors can target them.
   - Include representative placeholder content (realistic labels, a few
     list items, example data) that reflects what a real user would see.
   - Do NOT include any JavaScript.  State changes (open/close panels,
     active states, etc.) will be driven by guidestar's CSS-class-toggle
     actions, so model both the default state and the toggled state purely
     in CSS using class variants (e.g. .panel, .panel.open).

   Suggested approach:
   1. Read the top-level Vue components (App.vue, Layout.vue, or equivalent)
      to understand the overall shell structure.
   2. Read the component files for the toolbar, sidebar, and main content
      area to extract colours (check tailwind.config.js, tokens, or CSS
      custom properties), spacing, and element structure.
   3. Read any existing Storybook stories or test fixtures for realistic
      sample data.
   4. Produce wireframe.html.

   Focus on the layout skeleton and interactive affordances rather than
   pixel-perfect fidelity.  The wireframe does not need to be functional —
   it only needs to look convincing when static CSS classes are toggled.


From a live web URL
--------------------

Use this prompt when you have access to a running instance of the application
and want the agent to render the page and reproduce it as a wireframe.  The
prompt instructs the agent to use Playwright at a full laptop viewport,
capture all meaningful UI states, inline icons and images, reproduce
hover/click/interaction styles, and sanitize any external calls.

Because the wireframe is designed at a specific viewport width, use the
``:viewport:`` directive option (e.g. ``:viewport: 1440``) so guidestar
scales it correctly at any container size.

.. code-block:: text

   You are helping me build a guidestar wireframe — a self-contained HTML
   mockup used to animate a UI demo in documentation.

   Please prompt for a URL and then produce a single file called wireframe.html that reproduces the
   layout, visual style, and interactive affordances of that page.

   Follow these steps:

   1. **Render the page at a laptop viewport and capture each meaningful state.**
      Launch Playwright with a viewport of 1440 × 900 (a standard laptop
      resolution).  Navigate to the URL and wait for network-idle.
      Then *interact* with the page to reach each meaningful UI state
      (open a panel, submit a search, expand a dropdown, etc.) and take a
      full-page screenshot of each state.  These screenshots are your
      reconstruction reference.  Note the exact viewport width (1440) —
      you will need to record it so the guidestar directive can be told to
      render the wireframe at that width and scale it to fit.

   2. **Extract colours, spacing, and typography from rendered elements.**
      Do NOT attempt to fetch and inline external stylesheets.  Modern
      JavaScript frameworks inject all CSS at runtime; there are no static
      sheets to fetch.  Instead, call ``window.getComputedStyle()`` on a
      representative sample of elements (header, body background, buttons,
      input fields, table rows, badges, status bars) to read the actual
      background colours, text colours, border colours, border radii, font
      families, font sizes, and padding.  Collect these values in a
      palette table before writing any CSS.

   3. **Capture and inline custom icons and images.**
      For each non-text icon or image visible on the page:
        a. Try ``page.evaluate()`` to read any inline SVG source directly
           from the DOM (``el.outerHTML`` for ``<svg>`` elements, or
           ``el.src`` / ``el.currentSrc`` for ``<img>``).
        b. **Prefer SVG over raster formats.**  If the source image is a
           PNG, GIF, or JPEG, do **not** inline it as a base64 ``data:``
           URI — instead redraw it as a minimal inline SVG that reproduces
           the shape, colours, and general composition.  Raster images
           (especially GIFs) may be animated; a static wireframe only ever
           shows one frame, which is often incomplete.  Use the Playwright
           screenshot of the rendered element as your visual reference.
           Only fall back to a base64 ``data:`` URI if the image cannot be
           reasonably approximated as SVG (e.g. a photographic background).
           In that case apply the ~20 KB size limit from the previous rule.
        c. For icon-font glyphs (Material Icons, Font Awesome, etc.), look up
           the rendered text content or ``aria-label`` and substitute an
           equivalent unicode character or a minimal inline SVG path.

   4. **Capture hover, focus, and click interaction styles.**
      For each interactive element (buttons, links, checkboxes, tabs,
      dropdowns):
        a. Use ``page.hover(selector)`` to trigger the hover state, then
           read ``getComputedStyle()`` for background, border, and text
           colour changes.  Add a ``:hover`` rule (or a ``.hover`` class
           variant) that reproduces these.
        b. Use ``page.focus(selector)`` similarly to capture focus rings.
        c. For click/active states, read any CSS ``transition`` and
           ``animation`` properties and reproduce them with equivalent
           ``@keyframes`` or ``transition`` declarations in the wireframe.
        d. For dropdowns: click the trigger element to open the dropdown,
           capture the fully-rendered option list (text content, selected
           state, colours), and model the open state as a CSS class variant
           (e.g. ``.dropdown.open .dropdown-menu { display: block; }``).
           Hard-code the option list HTML with the real values from the page.
      These interaction styles should be pure CSS — no JavaScript.

   5. **Reconstruct HTML from scratch — do not copy the rendered DOM.**
      Framework SPAs produce thousands of lines of auto-generated wrappers.
      Use the screenshots, the computed-style palette, and the accessibility
      tree snapshot as references, then write clean minimal HTML from scratch
      that reproduces the layout visible in the screenshots.

      Pay special attention to **sticky/fixed bars** (headers, footers,
      toolbars that remain on screen while the main content scrolls).
      These are easy to under-represent because they sit outside the
      scrollable area and may be partially off-screen when you take a
      full-page screenshot.  For each bar:

      - Take a dedicated screenshot of the bar at full viewport width
        before reconstructing it.  List every control it contains,
        including secondary buttons that flank the primary action — they
        are easy to miss if you only read the DOM without looking.
      - Reproduce relative button widths faithfully: use ``flex: 1`` (or
        equivalent proportional sizing) on buttons that visually dominate
        the row; avoid fixed padding values that produce wrong proportions
        at different container widths.
      - If a status or summary line appears on a separate row within the
        bar, render it as a distinct child element beneath the button row,
        not as an inline sibling in the same flex row.

   6. **Add IDs to interactive elements.**
      For every button, input, select, tab, accordion, and toggleable panel,
      ensure there is a unique ``id`` attribute so that guidestar step
      selectors can target them.

   7. **Model multi-state UI with root-level class toggles.**
      For each distinct page state (search form vs. results, panel open vs.
      closed, banner visible vs. dismissed), define a CSS class on the root
      element that switches the layout::

        /* default */
        .results-view { display: none; }
        .search-view  { display: flex; }

        /* results state — toggled by add-class on #app */
        #app.results-open .search-view  { display: none; }
        #app.results-open .results-view { display: flex; }

      Do NOT use JavaScript.

   8. **Sanitize external references.**
      - Remove or stub out all ``<script>`` tags (inline and external).
      - Replace ``href`` / ``action`` on ``<a>`` and ``<form>`` with ``"#"``.
      - Remove all event-handler attributes (``onclick``, ``onsubmit``, etc.).
      - Replace any remaining external image URLs with neutral placeholders
        (light-grey background or inline SVG) if not already inlined in
        step 3.
      - Remove ``<meta http-equiv="...">`` refresh or CSP tags.
      - Double-check: no ``fetch()``, ``XMLHttpRequest``, or ``WebSocket``
        calls should remain (there should be none after removing scripts).

   9. **Write wireframe.html.**
      One self-contained HTML file: single ``<style>`` block in ``<head>``,
      no ``<script>`` tags, no external stylesheets, no external images or
      fonts.  Record the viewport width used (``1440``) in a comment at the
      top of the file so the guidestar ``:viewport:`` option can be set
      correctly.

   Verify by opening wireframe.html in a browser at 1440 × 900 and
   comparing it against each Playwright screenshot.  The two should look
   substantially the same.

   Verify the output by opening wireframe.html in a browser and comparing it
   visually against the Playwright screenshots for each state.  The two
   should look substantially the same at the same viewport size.
