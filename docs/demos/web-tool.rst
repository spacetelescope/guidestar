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

Step 1 — Load a source
~~~~~~~~~~~~~~~~~~~~~~~

Enter a URL pointing to a wireframe HTML file, a hosted demo page, or paste
a Sphinx directive block, then click **Load**.  The tool fetches the content
and shows a coloured badge indicating what it found:

- **Wireframe** — a plain HTML file to record steps against.
- **Demo (HTML)** — an existing ``data-guidestar-config`` page; options and
  steps are pre-populated automatically.
- **Demo (Sphinx)** — a ``.. guidestar-demo::`` directive block; steps and
  options are parsed and pre-populated.

.. raw:: html

   <iframe src="https://spacetelescope.github.io/guidestar/demos/web-tool/step-1.html"
           style="width:100%;height:320px;border:none;display:block" loading="lazy"
           title="Demo: Load a source"></iframe>


Step 2 — Set demo options
~~~~~~~~~~~~~~~~~~~~~~~~~~

Expand the **Demo Options** panel to configure the demo before recording.
Key settings include ``height`` (the container height in CSS units),
``viewport`` (the pixel width the wireframe was designed at — enables scale
mode), and toggles for ``repeat``, ``cursor``, and ``timeline``.

.. raw:: html

   <iframe src="https://spacetelescope.github.io/guidestar/demos/web-tool/step-2.html"
           style="width:100%;height:380px;border:none;display:block" loading="lazy"
           title="Demo: Set demo options"></iframe>


Step 3 — Record steps
~~~~~~~~~~~~~~~~~~~~~~

Click **Enable Record Mode** — the wireframe area gains a red border and a
*Recording* badge.  Click any element inside the wireframe and a popup
appears.  Choose the CSS selector from the ranked list of candidates, pick
an action (``click``, ``type-text``, ``add-class``, etc.), set the delay and
an optional caption, then click **Add Step**.

.. raw:: html

   <iframe src="https://spacetelescope.github.io/guidestar/demos/web-tool/step-3.html"
           style="width:100%;height:520px;border:none;display:block" loading="lazy"
           title="Demo: Record steps"></iframe>


Step 4 — Edit steps
~~~~~~~~~~~~~~~~~~~~

After recording, each step appears as a numbered card in the **Steps**
panel.  You can adjust the selector, action, value, delay, caption, and
caption position directly in each card.  Drag cards to reorder, or use
the ↑/↓ buttons.  Use **+ Add step manually** to insert a step without
clicking in the wireframe.

If an imported step targets a selector that no longer exists in the loaded
wireframe, the card shows a red **⚠ Invalid selector** badge — see
`Editing Existing Demos`_ for the replacement flow.

.. raw:: html

   <iframe src="https://spacetelescope.github.io/guidestar/demos/web-tool/step-4.html"
           style="width:100%;height:400px;border:none;display:block" loading="lazy"
           title="Demo: Edit steps"></iframe>


Step 5 — Preview
~~~~~~~~~~~~~~~~~

Expand the **Preview Demo** panel and click **Render Preview** to play the
demo in full using the live guidestar player.  After editing steps, click
**Render Preview** again to refresh.

.. raw:: html

   <iframe src="https://spacetelescope.github.io/guidestar/demos/web-tool/step-5.html"
           style="width:100%;height:280px;border:none;display:block" loading="lazy"
           title="Demo: Preview"></iframe>


Step 6 — Copy output
~~~~~~~~~~~~~~~~~~~~~

The **Output** panel shows the ready-to-use code.  Switch between the
**HTML** and **Sphinx Directive** tabs, then click **Copy** to copy it to
the clipboard and paste it directly into your page or ``.rst`` file.

.. raw:: html

   <iframe src="https://spacetelescope.github.io/guidestar/demos/web-tool/step-6.html"
           style="width:100%;height:340px;border:none;display:block" loading="lazy"
           title="Demo: Copy output"></iframe>


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
