.. _rf-capture:

Robot Framework Capture
=======================

The Robot Framework capture pipeline lets you build Guidestar demos from any
live web application — including JavaScript SPAs on external origins that
cannot be loaded via ``htmlSrc`` — without modifying the application itself.

Instead of injecting the live page at view time, the pipeline:

1. **Drives a real Chromium browser** (via Playwright) at build time.
2. **Intercepts API calls** with mock responses using Playwright's
   ``page.route()`` — at the network layer, not the JS layer, so it works
   regardless of whether the app uses ``fetch``, XHR, Axios, or WebSocket.
3. **Captures the page state** at each marked step as either a full-viewport
   screenshot or a cleaned DOM snapshot.
4. **Writes a static wireframe** HTML file plus a Guidestar JSON demo config.

The result feeds directly into the existing ``guidestar-build`` pipeline.
Readers of the documentation never contact the live application.

When to use this
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Approach
     - Best for
     - Limitations
   * - :doc:`manual`
     - Full design control; complex interactions
     - Must be maintained as UI evolves
   * - :doc:`live-url`
     - Simple, same-origin, ``fetch``-based pages
     - Cannot load external SPAs; CORS restriction
   * - :doc:`ai-assisted-url`
     - Quick wireframe from a URL via AI
     - Requires AI agent; no real interactivity
   * - **Robot Framework Capture** *(this page)*
     - Complex SPAs, external origins, real API mocking
     - Requires Playwright + RF at build time; screenshots are not
       interactively element-selectable in Guidestar cursor mode


Installation
------------

Install the ``capture`` extras and the Chromium browser:

.. code-block:: bash

   pip install "sphinx-guidestar[capture]"
   playwright install chromium

This adds two new dependencies to the existing environment:

* `Playwright <https://playwright.dev/python/>`_ (already required by
  ``guidestar-record`` for GIF recording)
* `Robot Framework <https://robotframework.org/>`_ ≥ 6.0


Capture modes
-------------

Both modes are available via the ``capture_mode`` Library argument (or the
``--mode`` CLI flag):

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Mode
     - What is captured
     - Notes
   * - ``screenshot`` *(default)*
     - Full-viewport PNG at each step, base64-embedded in the wireframe.
     - Always works regardless of origin or SPA complexity.  Guidestar cursor
       targets the root container, not individual UI elements.
   * - ``dom``
     - Live DOM serialised via ``page.content()``.  External stylesheets are
       fetched and inlined; external images become data URIs; ``<script>``
       tags are stripped.  Each state is namespaced under a ``data-gs-capture``
       attribute to prevent CSS conflicts.
     - Preserves the real DOM so Guidestar can target individual elements
       with CSS selectors.  CSS completeness depends on the application;
       fonts loaded via external URLs may be absent.


Writing a .robot file
----------------------

The ``GuidestarCapture`` Robot Framework library provides a set of keywords
that map directly to Playwright actions plus the two capture-specific
operations (``Capture Step`` and ``Export Demo``).

Minimal skeleton
~~~~~~~~~~~~~~~~

.. code-block:: robotframework
   :caption: ``examples/rf/my-demo.robot``

   *** Settings ***
   Library    guidestar.rf.GuidestarCapture
   ...    capture_mode=screenshot
   ...    viewport=1440
   ...    height=700px

   *** Variables ***
   ${APP_URL}      https://example.com/myapp
   ${MOCK_FILE}    ${CURDIR}/mock-data.json

   *** Test Cases ***
   My Feature Demo
       Open Capture    ${APP_URL}
       Route API       **/api/search**    body_file=${MOCK_FILE}
       Wait For Selector    #search-input
       Capture Step    caption=The search form    delay=2500
       Fill Text       #search-input    hello world
       Click Element   button[type="submit"]
       Wait For Selector    .results-table
       Capture Step    caption=Search results    delay=3000
       Export Demo     my-feature-demo    out_dir=examples/wireframes

Full Package Registry example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``examples/rf/`` directory contains a complete working example using
``examples/rf/live-app.html`` — a Package Registry search page whose API
call is intercepted with mock data from ``examples/rf/packages-mock.json``.
The sequence captures three steps: the initial search form, a query entered,
and the mock search results.

.. code-block:: robotframework
   :caption: ``examples/rf/open-library-screenshot.robot``

   *** Settings ***
   Library    guidestar.rf.GuidestarCapture
   ...    capture_mode=screenshot
   ...    viewport=960
   ...    height=460px

   *** Variables ***
   ${APP_URL}     file://${CURDIR}/live-app.html
   ${MOCK_FILE}   ${CURDIR}/packages-mock.json
   ${SEL_BTN}     \#pkg-btn
   ${SEL_INPUT}   \#pkg-input
   ${SEL_RESULT}  .result-card

   *** Test Cases ***
   Package Registry Search Screenshot Demo
       Route API    **/api/packages**    body_file=${MOCK_FILE}

       Open Capture    ${APP_URL}    wait_until=load
       Wait For Selector    ${SEL_BTN}    timeout=5000

       Capture Step
       ...    caption=^Package Registry Search
       ...    delay=2000

       Fill Text    ${SEL_INPUT}    astronomy
       Wait For Timeout    300
       Capture Step
       ...    caption=Type a search query
       ...    delay=2000

       Click Element    ${SEL_BTN}
       Wait For Selector    ${SEL_RESULT}    timeout=6000
       Capture Step
       ...    caption=Results served from mock data \u2014 no real API request was made
       ...    delay=3500

       Export Demo
       ...    open-library-screenshot
       ...    out_dir=${CURDIR}/../wireframes
       ...    standalone=True

.. note::

   ID selectors starting with ``#`` must be escaped as ``\#`` in Robot
   Framework because ``#`` starts an inline comment.  Assign them to
   ``${SEL_*}`` variables and reference the variables in keyword calls.

Mock data format
~~~~~~~~~~~~~~~~

The ``body_file`` argument points to a JSON file containing the **complete
response body** that the application's ``.then(r => r.json())`` chain
receives — it must match exactly what the real API returns.

For the Package Registry example the mock returns a JSON object with a
``packages`` array:

.. code-block:: json

   {
     "packages": [
       {"name": "astropy", "description": "...", "version": "6.1.0", "language": "Python"},
       {"name": "numpy",   "description": "...", "version": "2.0.1", "language": "Python"}
     ]
   }

For a real application such as the MAST JWST search, inspect the live API
with browser DevTools and replicate the response envelope exactly.  The full
fixture for five NGC 1300 JWST observations is in
``examples/rf/mast-jwst-mock.json``.


Live examples
--------------

Both demos below were produced from the same ``examples/rf/live-app.html``
Package Registry page using the two capture modes.  The ``.robot`` files
are in ``examples/rf/`` and the wireframes were generated locally with:

.. code-block:: bash

   guidestar-capture examples/rf/open-library-screenshot.robot \
       --out examples/wireframes --standalone

   guidestar-capture examples/rf/open-library-dom.robot \
       --out examples/wireframes --standalone

**Screenshot mode** — each step is a pixel-perfect PNG; the cursor points to
the root container.  The wireframe is 105 KB (three screenshots, base64-encoded).

.. raw:: html

   <iframe
     src="https://spacetelescope.github.io/guidestar/demos/rf-capture/screenshot-demo.html"
     style="width:100%;height:460px;border:none;display:block"
     loading="lazy"
     title="RF capture demo — screenshot mode"></iframe>

**DOM mode** — the captured DOM is preserved; real element selectors work,
text is selectable, and the layout is responsive.  The wireframe is 15 KB
(cleaned HTML, no images embedded).

.. raw:: html

   <iframe
     src="https://spacetelescope.github.io/guidestar/demos/rf-capture/dom-demo.html"
     style="width:100%;height:460px;border:none;display:block"
     loading="lazy"
     title="RF capture demo — DOM mode"></iframe>

Notice that in the DOM demo the search input, button, and result cards are
real DOM elements that Guidestar's cursor can navigate to by CSS selector.
In the screenshot demo the cursor targets the root ``#gs-capture-root``
container rather than individual elements within the screenshot.


Running the capture
--------------------

.. code-block:: bash

   # Basic run — output goes to same dir as the .robot file
   guidestar-capture examples/rf/open-library-screenshot.robot

   # Specify output dir and generate a standalone HTML page
   guidestar-capture examples/rf/open-library-screenshot.robot \
       --out examples/wireframes \
       --standalone

   # DOM mode
   guidestar-capture examples/rf/open-library-dom.robot \
       --mode dom \
       --out examples/wireframes \
       --standalone

   # Override viewport and height without editing the .robot file
   guidestar-capture examples/rf/open-library-screenshot.robot \
       --viewport 1280 --height 600px \
       --out /tmp/test-capture

The command writes to the output directory:

.. code-block:: text

   examples/wireframes/
     open-library-screenshot.html      ← wireframe HTML (screenshot or DOM)
     open-library-screenshot.json      ← Guidestar demo config
     open-library-screenshot-standalone.html  ← self-contained page (--standalone)
     _capture_output/                  ← Robot Framework logs (log.html, report.html)

Robot Framework also writes ``log.html`` and ``report.html`` to the
``_capture_output/`` subdirectory so you can inspect each step if a
selector fails.


Understanding the output
-------------------------

Wireframe HTML
~~~~~~~~~~~~~~

In **screenshot mode** the wireframe is a CSS-toggle slideshow.  Each
captured step is a ``<div class="gs-slide">`` containing a base64-encoded
``<img>``.  Only the active slide is visible; Guidestar switches slides by
toggling a class on the root element:

.. code-block:: html

   <div id="gs-capture-root" class="gs-slide-active-0">
     <div class="gs-slide" data-slide="0">
       <img src="data:image/png;base64,..." style="width:100%;display:block">
     </div>
     <div class="gs-slide" data-slide="1">
       <img src="data:image/png;base64,...">
     </div>
   </div>
   <style>
     .gs-slide { display: none; }
     #gs-capture-root.gs-slide-active-0 [data-slide="0"] { display: block; }
     #gs-capture-root.gs-slide-active-1 [data-slide="1"] { display: block; }
   </style>

In **DOM mode** each state is a namespaced ``<div data-gs-capture="N">``
wrapper containing the full cleaned DOM for that step.  CSS rules from each
state are prefixed with ``[data-gs-capture="N"]`` to prevent conflicts.

Demo JSON config
~~~~~~~~~~~~~~~~

The generated ``{name}.json`` uses multi-action steps that toggle the active
slide class:

.. code-block:: javascript

   {
     "wireframe": "open-library-screenshot.html",
     "title": "Open Library Screenshot",
     "height": "460px",
     "viewport": 960,
     "repeat": true,
     "steps": [
       {
         "actions": [
           {"target": "#gs-capture-root", "action": "remove-class", "value": "gs-slide-active-0"},
           {"target": "#gs-capture-root", "action": "add-class",    "value": "gs-slide-active-1"}
         ],
         "delay": 2000,
         "caption": "Type a search query"
       }
     ]
   }

This config is compatible with ``guidestar-build`` unchanged — no new
actions, no controller changes.

Embedding in docs
~~~~~~~~~~~~~~~~~

Use the generated ``{name}-standalone.html`` (``--standalone``) in an
iframe:

.. code-block:: rst

   .. raw:: html

      <iframe src="https://yourorg.github.io/yourrepo/demos/open-library-screenshot-standalone.html"
              style="width:100%;height:460px;border:none;display:block"
              loading="lazy" title="Package Registry Search Demo"></iframe>


Building and deploying
-----------------------

The wireframe HTML and JSON config slot directly into the existing demo
build pipeline:

.. code-block:: bash

   # Capture (run once, or in CI before guidestar-build)
   guidestar-capture examples/rf/mast-jwst-search.robot \
       --out examples/wireframes

   # Build all demos (existing command — unchanged)
   guidestar-build \
       --configs-dir examples/wireframes \
       --wireframes-dir examples/wireframes \
       --out _site

For CI, add a capture step before the existing build step in your workflow:

.. code-block:: yaml
   :caption: ``.github/workflows/pages.yml`` (excerpt)

   - name: Install capture dependencies
     run: |
       pip install -e ".[capture]"
       playwright install chromium --with-deps

   - name: Capture live-page demos
     run: |
       guidestar-capture examples/rf/open-library-screenshot.robot \
           --out examples/wireframes
       guidestar-capture examples/rf/open-library-dom.robot \
           --out examples/wireframes

   - name: Build self-contained demo pages
     run: |
       guidestar-build \
           --configs-dir examples/demos \
           --wireframes-dir examples/wireframes \
           --out _site


Keyword reference
-----------------

.. list-table::
   :header-rows: 1
   :widths: 25 45 30

   * - Keyword
     - Arguments
     - Notes
   * - ``Open Capture``
     - ``url``, ``viewport=1440``, ``height="700px"``,
       ``wait_until="networkidle"``
     - Launches Chromium, applies any previously registered routes,
       navigates to *url*.
   * - ``Route API``
     - ``url_pattern``, ``status=200``, ``body=None``,
       ``body_file=None``, ``content_type="application/json"``
     - Intercepts matching requests.  Can be called before or after
       ``Open Capture``.  Uses Playwright glob patterns.
   * - ``Fill Text``
     - ``selector``, ``value``
     - Clears then types *value* into the matched input.
   * - ``Click Element``
     - ``selector``
     - Clicks the first matching element.
   * - ``Wait For Selector``
     - ``selector``, ``timeout=10000``, ``state="visible"``
     - Waits until the selector is in the given state.
   * - ``Scroll Into View``
     - ``selector``
     - Scrolls the matching element into the viewport.
   * - ``Wait For Timeout``
     - ``ms``
     - Pauses for *ms* milliseconds (use sparingly — prefer
       ``Wait For Selector`` where possible).
   * - ``Evaluate``
     - ``expression``
     - Executes a JavaScript expression in the page context.
       Returns the result.
   * - ``Capture Step``
     - ``caption=""``, ``delay=2000``
     - Captures the current state as a demo step.
   * - ``Export Demo``
     - ``name``, ``out_dir="."`` , ``rst=False``,
       ``standalone=False``
     - Writes all output files and closes the browser.
   * - ``Close Capture``
     - —
     - Closes the browser (called automatically by ``Export Demo``).


MAST JWST Search — live example
---------------------------------

The demos below were produced by running ``examples/rf/mast-jwst-search.robot``
and ``examples/rf/mast-jwst-dom.robot`` against the real
`MAST JWST Observation Search <https://mast.stsci.edu/search/ui/#/jwst>`_ page
at build time.  The search API (``POST /search/jwst/api/v0.1/search``) was
intercepted using five real NGC 1300 observations from
``examples/rf/mast-jwst-mock.json``.  No live MAST server is contacted during
playback.  Expand the disclosure below each demo to see the ``.robot`` file
and CLI command needed to reproduce it.

**Screenshot mode** — pixel-perfect captures at 1440 × 720.

.. raw:: html

   <iframe
     src="https://spacetelescope.github.io/guidestar/demos/mast-jwst/screenshot-demo.html"
     style="width:100%;height:720px;border:none;display:block"
     loading="lazy"
     title="MAST JWST Search — screenshot mode"></iframe>

.. raw:: html

   <details style="margin:1rem 0 1.5rem;border:1px solid var(--pst-color-border,#e2e8f0);border-radius:6px;overflow:hidden">
   <summary style="cursor:pointer;padding:0.55rem 1rem;background:var(--pst-color-surface,#f8fafc);font-weight:600;font-size:0.875rem;user-select:none;list-style:none;display:flex;align-items:center;gap:0.5rem">
     <span style="color:#6366f1;font-size:0.75rem">&#9658;</span>&nbsp;
     Reproduce this demo — <code style="font-size:0.8rem">examples/rf/mast-jwst-search.robot</code>
   </summary>
   <div style="padding:1rem;border-top:1px solid var(--pst-color-border,#e2e8f0)">
   <p style="margin:0 0 0.4rem;font-size:0.8rem;color:var(--pst-color-muted,#64748b)">
     Prerequisites:&nbsp;<code>pip install &quot;sphinx-guidestar[capture]&quot; &amp;&amp; playwright install chromium</code></p>

.. code-block:: robotframework

   *** Settings ***
   Documentation    Screenshot-mode capture of MAST JWST Observation Search.

   Library    guidestar.rf.GuidestarCapture
   ...    capture_mode=screenshot
   ...    viewport=1440
   ...    height=720px

   *** Variables ***
   ${MAST_URL}      https://mast.stsci.edu/search/ui/#/jwst
   ${MOCK_FILE}     ${CURDIR}/mast-jwst-mock.json
   ${SEL_INPUT}     \#target-name-input
   ${SEL_SEARCH}    button.v-btn--block

   *** Test Cases ***
   MAST JWST Search Screenshot
       Route API    **/search/jwst/api/v0.1/search**    body_file=${MOCK_FILE}

       Open Capture    ${MAST_URL}    wait_until=networkidle
       Wait For Selector    ${SEL_INPUT}    timeout=20000
       Wait For Timeout    500

       Capture Step
       ...    caption=^The JWST Observation Search form
       ...    delay=2500

       Click Element    ${SEL_INPUT}
       Wait For Timeout    200
       Fill Text    ${SEL_INPUT}    NGC 1300
       Wait For Timeout    800
       Capture Step
       ...    caption=Enter an object name or sky coordinates
       ...    delay=2200

       Click Element    ${SEL_SEARCH}
       Wait For Timeout    4000
       Capture Step
       ...    caption=Search results load from the mock API
       ...    delay=3500

       Evaluate    window.scrollTo(0, 600)
       Wait For Timeout    600
       Capture Step
       ...    caption=Scroll through the observation list
       ...    delay=2500

       Export Demo
       ...    mast-jwst-search
       ...    out_dir=${CURDIR}/../../examples/wireframes
       ...    standalone=True

.. raw:: html

   <p style="margin:0.75rem 0 0.25rem;font-size:0.8rem;font-weight:600">CLI command:</p>
   <pre style="background:#1e1e2e;color:#cdd6f4;padding:0.6rem 1rem;border-radius:6px;font-size:0.78rem;overflow-x:auto;margin:0 0 0.5rem"><code>guidestar-capture examples/rf/mast-jwst-search.robot \
    --out examples/wireframes --standalone</code></pre>
   <p style="margin:0.5rem 0 0;font-size:0.78rem;color:var(--pst-color-muted,#64748b)">Mock fixture: <code>examples/rf/mast-jwst-mock.json</code> — five real NGC 1300 JWST observations in the live MAST API envelope.</p>
   </div></details>

**DOM mode** — the captured Vuetify DOM is preserved with real table markup,
column headers, and result rows.

.. raw:: html

   <iframe
     src="https://spacetelescope.github.io/guidestar/demos/mast-jwst/dom-demo.html"
     style="width:100%;height:720px;border:none;display:block"
     loading="lazy"
     title="MAST JWST Search — DOM mode"></iframe>

.. raw:: html

   <details style="margin:1rem 0 1.5rem;border:1px solid var(--pst-color-border,#e2e8f0);border-radius:6px;overflow:hidden">
   <summary style="cursor:pointer;padding:0.55rem 1rem;background:var(--pst-color-surface,#f8fafc);font-weight:600;font-size:0.875rem;user-select:none;list-style:none;display:flex;align-items:center;gap:0.5rem">
     <span style="color:#6366f1;font-size:0.75rem">&#9658;</span>&nbsp;
     Reproduce this demo — <code style="font-size:0.8rem">examples/rf/mast-jwst-dom.robot</code>
   </summary>
   <div style="padding:1rem;border-top:1px solid var(--pst-color-border,#e2e8f0)">
   <p style="margin:0 0 0.4rem;font-size:0.8rem;color:var(--pst-color-muted,#64748b)">
     Prerequisites:&nbsp;<code>pip install &quot;sphinx-guidestar[capture]&quot; &amp;&amp; playwright install chromium</code></p>

.. code-block:: robotframework

   *** Settings ***
   Documentation    DOM-mode capture of MAST JWST Observation Search.

   Library    guidestar.rf.GuidestarCapture
   ...    capture_mode=dom
   ...    viewport=1440
   ...    height=720px

   *** Variables ***
   ${MAST_URL}      https://mast.stsci.edu/search/ui/#/jwst
   ${MOCK_FILE}     ${CURDIR}/mast-jwst-mock.json
   ${SEL_INPUT}     \#target-name-input
   ${SEL_SEARCH}    button.v-btn--block

   *** Test Cases ***
   MAST JWST Search Screenshot
       Route API    **/search/jwst/api/v0.1/search**    body_file=${MOCK_FILE}

       Open Capture    ${MAST_URL}    wait_until=networkidle
       Wait For Selector    ${SEL_INPUT}    timeout=20000
       Wait For Timeout    500

       Capture Step
       ...    caption=^The JWST Observation Search form
       ...    delay=2500

       Click Element    ${SEL_INPUT}
       Wait For Timeout    200
       Fill Text    ${SEL_INPUT}    NGC 1300
       Wait For Timeout    800
       Capture Step
       ...    caption=Enter an object name or sky coordinates
       ...    delay=2200

       Click Element    ${SEL_SEARCH}
       Wait For Timeout    4000
       Capture Step
       ...    caption=Search results load from the mock API
       ...    delay=3500

       Evaluate    window.scrollTo(0, 600)
       Wait For Timeout    600
       Capture Step
       ...    caption=Scroll through the observation list
       ...    delay=2500

       Export Demo
       ...    mast-jwst-dom
       ...    out_dir=${CURDIR}/../../examples/wireframes
       ...    standalone=True

.. raw:: html

   <p style="margin:0.75rem 0 0.25rem;font-size:0.8rem;font-weight:600">CLI command:</p>
   <pre style="background:#1e1e2e;color:#cdd6f4;padding:0.6rem 1rem;border-radius:6px;font-size:0.78rem;overflow-x:auto;margin:0 0 0.5rem"><code>guidestar-capture examples/rf/mast-jwst-dom.robot \
    --out examples/wireframes --standalone</code></pre>
   <p style="margin:0.5rem 0 0;font-size:0.78rem;color:var(--pst-color-muted,#64748b)">Same mock fixture as the screenshot demo. Only <code>capture_mode=dom</code> and the <code>Export Demo</code> output name differ.</p>
   </div></details>

