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

.. guidestar-demo:: _static/demo-builder-wireframe.html
   :viewport: 1440
   :height: 320px
   :repeat: false
   :init-steps-json: [{"target":"#section-source","action":"add-class","value":"expanded"}]
   :steps-json: [{"target":"#source-url-input","action":"highlight","delay":1200,"caption":"Enter the URL of your wireframe or existing demo"},{"target":"#btn-load","action":"highlight","delay":1200,"caption":"Click Load to fetch and auto-detect the source"},{"target":"#section-source","action":"add-class","value":"loaded","delay":500,"noHighlight":true},{"target":"#source-badge","action":"highlight","delay":1200,"caption":"A badge confirms the detected type — Wireframe, Demo (HTML), or Demo (Sphinx)"}]


Step 2 — Set demo options
~~~~~~~~~~~~~~~~~~~~~~~~~~

Expand the **Demo Options** panel to configure the demo before recording.
Key settings include ``height`` (the container height in CSS units),
``viewport`` (the pixel width the wireframe was designed at — enables scale
mode), and toggles for ``repeat``, ``cursor``, and ``timeline``.

.. guidestar-demo:: _static/demo-builder-wireframe.html
   :viewport: 1440
   :height: 380px
   :repeat: false
   :init-steps-json: [{"target":"#section-options","action":"add-class","value":"expanded"}]
   :steps-json: [{"target":"#options-header","action":"highlight","delay":800,"caption":"The Demo Options panel — configure height, viewport, and playback settings"},{"target":"#opt-height","action":"highlight","delay":1200,"caption":"Set the container height (e.g. 480px)"},{"target":"#opt-viewport","action":"highlight","delay":1200,"caption":"Set the viewport width to enable scale mode"},{"target":"#opt-repeat","action":"highlight","delay":1000,"caption":"Toggle repeat, cursor, timeline, and other options"}]


Step 3 — Record steps
~~~~~~~~~~~~~~~~~~~~~~

Click **Enable Record Mode** — the wireframe area gains a red border and a
*Recording* badge.  Click any element inside the wireframe and a popup
appears.  Choose the CSS selector from the ranked list of candidates, pick
an action (``click``, ``type-text``, ``add-class``, etc.), set the delay and
an optional caption, then click **Add Step**.

.. guidestar-demo:: _static/demo-builder-wireframe.html
   :viewport: 1440
   :height: 520px
   :repeat: true
   :init-steps-json: [{"target":"#section-recording","action":"add-class","value":"expanded"}]
   :steps-json: [{"target":"#btn-record","action":"click","delay":1000,"caption":"Click Enable Record Mode"},{"target":"#iframe-wrap","action":"add-class","value":"recording","delay":800,"noHighlight":true},{"target":"#record-status","action":"add-class","value":"recording","delay":200,"noHighlight":true},{"target":"#btn-record","action":"set-text","value":"Stop Recording","delay":200,"noHighlight":true,"caption":"The wireframe gains a red border — click any element inside it"},{"target":"#btn-action","action":"highlight","delay":1400,"caption":"Clicking an element opens the step popup…"},{"target":"#action-modal","action":"add-class","value":"open","delay":600,"noHighlight":true},{"target":"#modal-selector","action":"highlight","delay":1200,"caption":"Choose the best selector from the ranked candidates"},{"target":"#modal-action","action":"highlight","delay":1000,"caption":"Pick an action: click, type-text, add-class, and more"},{"target":"#modal-caption","action":"highlight","delay":1000,"caption":"Add an optional caption to display during the step"},{"target":"#btn-add-step","action":"highlight","delay":1200,"caption":"Click Add Step to append it to the steps list"}]


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

.. guidestar-demo:: _static/demo-builder-wireframe.html
   :viewport: 1440
   :height: 520px
   :repeat: true
   :init-steps-json: [{"target":"#section-steps","action":"add-class","value":"expanded"},{"target":"#section-steps","action":"add-class","value":"has-steps"}]
   :steps-json: [{"target":"#step-list-content","action":"highlight","delay":1400,"caption":"Each recorded step appears as an editable card"},{"target":"#step-card-1","action":"highlight","delay":1400,"caption":"Edit the selector, action, delay, and caption inline"},{"target":"#step-card-2","action":"highlight","delay":1200,"caption":"Cards can be reordered by dragging or with the ↑/↓ buttons"},{"target":"#step-card-invalid","action":"highlight","delay":1600,"caption":"A red badge flags steps whose selector is missing from the wireframe"},{"target":"#btn-pick-replacement","action":"highlight","delay":1400,"caption":"Click Pick replacement, then click the correct element in the wireframe"},{"target":"#btn-add-manual","action":"highlight","delay":1200,"caption":"Or add a step manually without clicking in the wireframe"}]


Step 5 — Preview
~~~~~~~~~~~~~~~~~

Expand the **Preview Demo** panel and click **Render Preview** to play the
demo in full using the live guidestar player.  After editing steps, click
**Render Preview** again to refresh.

.. guidestar-demo:: _static/demo-builder-wireframe.html
   :viewport: 1440
   :height: 340px
   :repeat: true
   :init-steps-json: [{"target":"#section-preview","action":"add-class","value":"expanded"}]
   :steps-json: [{"target":"#preview-header","action":"highlight","delay":800,"caption":"The Preview Demo panel — play back the full demo in-place"},{"target":"#btn-render-preview","action":"highlight","delay":1400,"caption":"Click Render Preview to play back the demo using the live guidestar player"}]


Step 6 — Copy output
~~~~~~~~~~~~~~~~~~~~~

The **Output** panel shows the ready-to-use code.  Switch between the
**HTML** and **Sphinx Directive** tabs, then click **Copy** to copy it to
the clipboard and paste it directly into your page or ``.rst`` file.

.. guidestar-demo:: _static/demo-builder-wireframe.html
   :viewport: 1440
   :height: 440px
   :repeat: true
   :init-steps-json: [{"target":"#section-output","action":"add-class","value":"expanded"}]
   :steps-json: [{"target":"#tab-html","action":"highlight","delay":1200,"caption":"The HTML tab shows a self-contained embed snippet"},{"target":"#tab-sphinx","action":"click","delay":1000,"caption":"Switch to the Sphinx Directive tab"},{"target":"#out-sphinx","action":"highlight","delay":1400,"caption":"The Sphinx tab shows a ready-to-paste .. guidestar-demo:: directive"},{"target":"#btn-copy","action":"highlight","delay":1200,"caption":"Click Copy to copy the output to the clipboard"}]


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
