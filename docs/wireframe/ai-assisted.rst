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

   1. **Render the page with Playwright.**
      Navigate to the URL with a Playwright browser instance.  Wait for the
      page to reach a network-idle state.  Take a full-page screenshot for
      reference and capture ``document.documentElement.outerHTML`` to get
      the fully-rendered DOM (including any content injected by JavaScript).

   2. **Extract and inline all styles.**
      For each external stylesheet loaded by the page, fetch its content and
      inline it as a <style> block.  Resolve any relative ``url()`` asset
      references; replace web-font ``@font-face`` declarations with
      equivalent system-font fallbacks.  Discard any ``@import`` rules that
      reference external origins.

   3. **Reproduce the layout skeleton.**
      From the rendered DOM and inlined styles, reconstruct the structural
      HTML — top bar, sidebars, content areas, footer, modals — preserving
      class names and nesting so that the visual appearance matches the
      screenshot.  You may simplify or remove purely decorative elements
      that do not contribute to the layout.

   4. **Add IDs to interactive elements.**
      For every button, input, select, tab, accordion, and toggleable panel,
      ensure there is a unique id attribute so that guidestar step selectors
      can target them.  If the element already has an id, keep it.

   5. **Model interactive states in CSS.**
      Identify elements that have open/closed, active/inactive, or
      visible/hidden variants.  Define CSS class variants for each state
      (e.g. ``.sidebar``, ``.sidebar.open``).  Do NOT use JavaScript.

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
      - Strip ``fetch``, ``XMLHttpRequest``, ``WebSocket``, and any other
        network calls that may appear in remaining inline scripts (there
        should be none after step 6a, but double-check).

   7. **Write wireframe.html.**
      The final file must be a single self-contained HTML file: one
      ``<style>`` block in ``<head>``, no ``<script>`` tags, no external
      stylesheet links, no external image or font references.  All content
      that was visible in the original page should be present as static HTML.

   Verify the output by opening wireframe.html in a browser and comparing it
   visually against the Playwright screenshot.  The two should look
   substantially the same at the same viewport size.
