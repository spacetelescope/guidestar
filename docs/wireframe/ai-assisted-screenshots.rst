AI Assisted from Screenshots
============================

Use this prompt when you have a series of screenshots that capture the steps
of a workflow — for example, a multi-step form, a search-and-results flow, or
a tool walkthrough — and you want an AI coding agent to turn them into a
guidestar wireframe.

Because the agent cannot inspect the live DOM, it works entirely from the
visual information in the screenshots.  The prompt asks it to reproduce the
layout and styling of each screen, identify the user action that moves from
one screen to the next (typing text, clicking a button, etc.), and encode
each screen as a CSS-class-toggled state in a single self-contained
``wireframe.html`` file.

Attach all screenshots before sending the prompt, and list the filenames in
order in the ``Attached screenshots`` section.  The agent will use that order
to determine the step sequence.

Because the wireframe is designed at a specific viewport width, use the
``:viewport:`` directive option (e.g. ``:viewport: 1440``) matching the
dimensions of your screenshots so guidestar scales it correctly at any
container size.

.. code-block:: text

   You are helping me build a guidestar wireframe — a self-contained HTML
   mockup used to animate a UI demo in documentation.

   Before starting, read the guidestar documentation to understand the
   wireframe format, step syntax, and available actions:
     Docs:   https://spacetelescope.github.io/guidestar/
     Steps:  https://spacetelescope.github.io/guidestar/demos/configuration.html
     GitHub: https://github.com/spacetelescope/guidestar

   I have attached a series of screenshots that show each step of a workflow.
   Please study them carefully and produce a single file called wireframe.html
   that reproduces every screen and the transitions between them.

   Attached screenshots (in order):
     [screenshot-01.png]  — brief label, e.g. "Empty search form"
     [screenshot-02.png]  — "User has typed a query in the search box"
     [screenshot-03.png]  — "Results panel is visible"
     … (continue for each screenshot)

   Replace the bracketed placeholders with your actual filenames and
   one-line descriptions before sending this prompt.

   ── Step 1: Identify each screen and the action between screens ────────────

   For each consecutive pair of screenshots, name:

   a. The **starting state** — what the UI looks like before the action.
   b. The **user action** that causes the transition.  Be specific:
        - Type text: name the field and the exact text entered, e.g.
          "Type 'NGC 1234' into the search input (#target-input)"
        - Click: name the button or link, e.g. "Click the 'Submit' button
          (#submit-btn)"
        - Select: name the dropdown and the chosen option, e.g.
          "Select 'JWST' from the instrument dropdown (#instrument-select)"
        - Scroll: note the direction and which panel scrolls, e.g.
          "Scroll the results list down by 200 px"
        - Hover: name the element, e.g. "Hover over the first result row"
        - Toggle: name the checkbox or switch, e.g.
          "Check the 'Show archived' checkbox (#show-archived)"
   c. The **resulting state** — what the UI looks like after the action
      (i.e. the next screenshot).

   Produce a short action table before writing any HTML:

     Step  | From state    | Action                        | To state
     -------|---------------|-------------------------------|------------
     1 → 2  | Empty form    | Type 'NGC 1234' in #target    | Filled form
     2 → 3  | Filled form   | Click #submit-btn             | Results view
     …

   ── Step 2: Extract colours, spacing, and typography ─────────────────────

   From the screenshots alone, derive a visual palette:

   - Background colours for the page, panels, headers, and cards.
   - Text colours for headings, body text, labels, and muted/secondary text.
   - Accent / brand colours used on primary buttons, links, and highlights.
   - Border colours and approximate border-radius values.
   - Font families: note any obvious sans-serif / monospace distinctions; use
     system-stack fallbacks (e.g. ``system-ui, sans-serif``) for all fonts.
   - Approximate padding and spacing rhythm (e.g. 8 px, 16 px, 24 px).

   Record this palette as a CSS custom-property block at the top of your
   ``<style>`` section so adjustments are easy later.

   ── Step 3: Reconstruct HTML from scratch ────────────────────────────────

   Write clean, minimal HTML that reproduces the layout visible in each
   screenshot.  Do NOT copy rendered framework DOM — use the screenshots as
   your sole reconstruction reference.

   Key conventions:

   - One top-level wrapper ``<div id="app">`` (or equivalent).
   - A single ``<style>`` block in ``<head>`` — no external stylesheets, no
     ``<link>`` tags, no ``@import``.
   - No ``<script>`` tags other than the small interaction-handler block
     described in step 5.
   - No external image URLs: replace photos or logos with a neutral
     placeholder (light-grey ``<div>`` or a minimal inline ``<svg>``), or
     redraw simple icons as inline SVG paths.
   - Give **every** button, input, select, tab, and toggleable panel a unique
     ``id`` attribute.  Guidestar step selectors use these IDs to target
     elements during the animated demo.

   Pay special attention to **scrollable regions** (result lists, data
   tables, long forms).  Apply the flex-containment pattern so they scroll
   correctly inside a constrained guidestar container:

     .app { height: 100%; min-height: 0; display: flex; flex-direction: column; }
     .scrollable-region { flex: 1; min-height: 0; overflow-y: auto; }
     .action-bar { flex-shrink: 0; }

   ── Step 4: Encode each screen as a CSS-class state ──────────────────────

   Every distinct screen from your action table becomes a CSS class on
   ``#app`` (or the root element).  Use the class to show/hide the right
   panels:

     /* default — step 1 state */
     .results-panel { display: none; }
     .search-panel  { display: flex; }

     /* step 3 state — toggled by guidestar add-class on #app */
     #app.results-open .search-panel  { display: none; }
     #app.results-open .results-panel { display: flex; }

   Use short, descriptive class names derived from the action table
   (e.g. ``results-open``, ``modal-visible``, ``confirm-step``).

   ── Step 5: Add lightweight interaction handlers ─────────────────────────

   At the bottom of ``<body>`` add a single ``<script>`` block that mirrors
   the CSS class toggles so a human clicking through the wireframe manually
   gets the same transitions guidestar produces automatically.  Use
   ``.onclick =`` (not ``addEventListener``) so guidestar can safely replay
   the block on restart without stacking duplicate listeners.  No ``fetch()``,
   timers, or DOM creation — class toggles only.

   Example:

     <script>
     document.getElementById('submit-btn').onclick = function () {
       document.getElementById('app').classList.add('results-open');
     };
     document.getElementById('clear-btn').onclick = function () {
       document.getElementById('app').classList.remove('results-open');
     };
     </script>

   ── Step 6: Add a step-comment block for the guidestar author ────────────

   Immediately before ``</body>``, add an HTML comment that lists the
   suggested guidestar steps, one per line, in the format the author can
   paste directly into their Sphinx directive:

     <!--  Suggested guidestar steps
     - caption: "Enter a target name"
       highlight: "#target-input"
       type-text:
         selector: "#target-input"
         text: "NGC 1234"

     - caption: "Click Submit to search"
       highlight: "#submit-btn"
       add-class:
         selector: "#app"
         class: "results-open"

     - caption: "Results are displayed"
       highlight: "#results-panel"
     -->

   Use the action table from step 1 to derive these steps.  The ``caption``
   should describe what the user is doing; ``highlight`` should point to the
   element being acted upon; the step type should match the action identified
   (``type-text``, ``add-class``, ``remove-class``, ``scroll``, etc.).

   ── Step 7: Verify and finalise ──────────────────────────────────────────

   After writing wireframe.html:

   1. Confirm each screenshot state can be reached by toggling the
      corresponding CSS class on the root element.
   2. Confirm every element referenced in the step-comment block has a
      matching ``id`` in the HTML.
   3. Note the pixel width that the screenshots appear to have been captured
      at (or your best estimate), and add it as a comment on the first line:

        <!-- viewport: 1440 -->

      The guidestar directive author should set ``:viewport: 1440`` (or the
      noted width) to ensure correct scaling at any container size.
