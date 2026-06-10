Interactive Web Tool
====================

The **Guidestar Demo Builder** is a browser-based tool for creating and
editing demos interactively — no code required.  It is hosted alongside
the live examples on GitHub Pages:

.. raw:: html

   <p>
     <a href="https://spacetelescope.github.io/guidestar/demo-builder/"
        target="_blank" rel="noopener"
        style="display:inline-flex;align-items:center;gap:0.4em;
               background:#6366f1;color:#fff;padding:0.45em 1em;
               border-radius:6px;font-weight:600;text-decoration:none;
               font-size:0.95em;">
       Open Demo Builder ↗
     </a>
   </p>


Workflow
--------

1. **Load a source** — Enter a URL (wireframe HTML, hosted demo page, or
   Sphinx ``.rst`` file) in the *Source* box and click **Load**.  The tool
   auto-detects what you have loaded and shows a coloured badge:

   - **Wireframe** — a plain HTML file to record steps against.
   - **Demo (HTML)** — an existing ``data-guidestar-config`` page; options
     and steps are pre-populated automatically.
   - **Demo (Sphinx)** — a ``.. guidestar-demo::`` directive; steps and
     options are parsed and pre-populated.

2. **Set demo options** — Expand the *Demo Options* panel to adjust the
   height, viewport width, repeat behaviour, cursor, timeline, and
   interaction settings.

3. **Record steps** — Click **Enable Record Mode**.  The wireframe gains a
   red border.  Click any element inside the wireframe: a popup appears so
   you can choose the selector, action, delay, and caption for that step.
   Click **Add Step** to append it to the list.  Click **Stop Recording**
   when done.

4. **Edit steps** — Each step appears as a card in the *Steps* panel.  You
   can change the selector, action, value, delay, caption, and caption
   position inline.  Drag cards to reorder, or use the ↑/↓ buttons.  Use
   **+ Add step manually** to insert a step without clicking in the
   wireframe.

5. **Preview** — Expand the *Preview Demo* panel and click **Render
   Preview** to play back the demo in full using the guidestar player.
   After editing steps, click **Render Preview** again to refresh.

6. **Copy output** — The *Output* panel shows the ready-to-use code.
   Switch between the **HTML** and **Sphinx Directive** tabs, then click
   **Copy** to copy it to the clipboard.  Paste it directly into your page
   or ``.rst`` file.


Editing Existing Demos
-----------------------

The tool doubles as a demo editor.  To modify an existing demo:

- **From a hosted HTML page** — paste or enter the URL of the demo page.
  The tool extracts the ``data-guidestar-config`` JSON, loads the
  wireframe, and pre-populates all options and steps.
- **From a Sphinx directive** — paste the ``.. guidestar-demo::`` block
  (including its options) into the text fallback area.  The tool parses
  `:steps-json:` (or the shorthand `:steps:` string) and fills in every
  step card.

**Invalid selectors** — if an imported step targets a CSS selector that
does not exist in the loaded wireframe (for example, the wireframe has
changed since the demo was first recorded), the step card is highlighted
with a red **⚠ Invalid selector** badge.

To fix it, click **Pick replacement** on that card.  The wireframe gains
a yellow border and a "Click to pick element" prompt.  Click the correct
element in the wireframe: the step's target is updated in place while its
action, delay, caption, and value are preserved.  Press ``Esc`` to cancel.


Cross-Origin Wireframes
------------------------

Browsers block cross-origin ``fetch()`` requests unless the server sends
CORS headers.  If you enter a URL that cannot be fetched directly, the
tool shows an explanation and reveals two fallback options:

- **Paste HTML** — copy the wireframe's source code and paste it into the
  text area.
- **Upload file** — use the file picker to load the ``.html`` file from
  your computer.

Both fallbacks inject the content identically to a direct fetch; recording
and validation work the same way.

.. note::

   Wireframes served from the same GitHub Pages site
   (``https://spacetelescope.github.io/guidestar/``) are same-origin and
   load without any CORS restriction.
