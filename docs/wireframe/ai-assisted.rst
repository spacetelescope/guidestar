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
   :repeat: true


From a Vue / JavaScript source repository
------------------------------------------

Use this prompt when the target application lives in a local or remote
repository built with Vue (or a similar component-based framework).  Adjust
the repository path and the list of components to focus on as needed.

.. code-block:: text

   You are helping me build a guidestar wireframe — a self-contained HTML
   mockup used to animate a UI demo in documentation.

   Please explore the repository at ../jdaviz (or the path I provide) and
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
prompt instructs the agent to use Playwright to capture the rendered DOM,
reproduce the styling faithfully, and sanitize any external links or API
calls so the resulting file is self-contained and safe to ship in docs.

.. code-block:: text

   You are helping me build a guidestar wireframe — a self-contained HTML
   mockup used to animate a UI demo in documentation.

   Please produce a single file called wireframe.html that reproduces the
   layout, visual style, and interactive affordances of the page at:

       <INSERT URL HERE>

   Follow these steps:

   1. **Render the page and capture each meaningful state.**
      Navigate to the URL with a Playwright browser instance and wait for
      network-idle.  Then *interact* with the page to reach each meaningful
      UI state (e.g. open a panel, submit a search, expand a drawer) and
      take a full-page screenshot of each state.  These screenshots are your
      reconstruction reference — do not rely on a single initial-load
      screenshot for a multi-state UI.

   2. **Extract colours and spacing from rendered elements.**
      Do NOT attempt to fetch and inline external stylesheets.  Modern
      JavaScript frameworks (Vue, React, Angular) inject all CSS at runtime
      via ``<style>`` tags generated by the bundler; there are no static
      stylesheets to fetch.  Instead, call ``window.getComputedStyle()`` on
      representative elements (header, body, buttons, table rows) to read
      the actual background colours, text colours, border colours, border
      radii, and font families that are visible on screen.  Use these values
      directly in your hand-written CSS.

   3. **Reconstruct HTML from scratch — do not copy the rendered DOM.**
      ``document.documentElement.outerHTML`` for a framework SPA produces
      thousands of lines of auto-generated class names and deeply nested
      wrappers that are not suitable for a wireframe.  Use it (and the
      accessibility tree snapshot) as a *reference* for element names,
      labels, and structure, then write clean, minimal HTML from scratch
      that reproduces the layout visible in the screenshots.

   4. **Add IDs to interactive elements.**
      For every button, input, select, tab, accordion, and toggleable panel,
      ensure there is a unique id attribute so that guidestar step selectors
      can target them.  If the element already has an id, keep it.

   5. **Model interactive states with root-level class toggles.**
      For each distinct UI state (search form vs. results table, panel open
      vs. closed, banner visible vs. dismissed), define a CSS class on the
      root element that switches the entire layout.  Example::

        /* default: show search form */
        .results-view  { display: none; }
        .search-view   { display: flex; }

        /* results state: toggled by adding .results-open to #app */
        #app.results-open .search-view  { display: none; }
        #app.results-open .results-view { display: flex; }

      This pattern lets a single guidestar ``add-class`` step on the root
      element transition the whole page between states.  Do NOT use
      JavaScript.

   6. **Sanitize external references.**
      - Remove or stub out all ``<script>`` tags (inline and external).
      - Replace all ``href`` and ``action`` attributes on ``<a>`` and
        ``<form>`` elements with ``href="#"`` / ``action="#"``.
      - Remove ``onclick``, ``onsubmit``, and all other event-handler
        attributes.
      - Replace ``<img src="...">`` references to external origins with a
        neutral placeholder (a light-grey ``background-color`` on the
        element, or an inline SVG placeholder).
      - Remove any ``<meta http-equiv="...">`` refresh or CSP tags.

   7. **Write wireframe.html.**
      The final file must be a single self-contained HTML file: one
      ``<style>`` block in ``<head>``, no ``<script>`` tags, no external
      stylesheet links, no external image or font references.  All content
      that was visible in the original page should be present as static HTML.

   Verify the output by opening wireframe.html in a browser and comparing it
   visually against the Playwright screenshots for each state.  The two
   should look substantially the same at the same viewport size.
