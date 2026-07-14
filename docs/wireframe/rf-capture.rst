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

Full MAST JWST example
~~~~~~~~~~~~~~~~~~~~~~~

The ``examples/rf/`` directory contains a complete example that drives the
MAST JWST Observation Search interface with mocked API responses.  The
sequence captures four steps: the initial search form, a target name
entered, the search results table, and a scrolled view of the results.

.. code-block:: robotframework
   :caption: ``examples/rf/mast-jwst-search.robot``

   *** Settings ***
   Library    guidestar.rf.GuidestarCapture
   ...    capture_mode=screenshot
   ...    viewport=1440
   ...    height=720px

   *** Variables ***
   ${MAST_JWST_URL}    https://mast.stsci.edu/search/ui/#/jwst
   ${MOCK_DATA_FILE}   ${CURDIR}/mast-jwst-mock.json

   ${SEL_TARGET_INPUT}    input[placeholder*="Target"]
   ${SEL_SEARCH_BUTTON}   button[type="submit"]
   ${SEL_RESULTS_TABLE}   .v-data-table__wrapper

   *** Test Cases ***
   MAST JWST Observation Search Demo
       Open Capture    ${MAST_JWST_URL}    wait_until=networkidle

       Route API
       ...    **/api/v0.1/missions/search**
       ...    body_file=${MOCK_DATA_FILE}

       Wait For Selector    ${SEL_TARGET_INPUT}    timeout=15000
       Capture Step    caption=^The JWST Observation Search form    delay=2500

       Fill Text    ${SEL_TARGET_INPUT}    NGC 1300
       Capture Step    caption=Enter a target name or sky coordinates    delay=2200

       Click Element    ${SEL_SEARCH_BUTTON}
       Wait For Selector    ${SEL_RESULTS_TABLE}    timeout=12000
       Capture Step    caption=Results load from the mock API    delay=3500

       Scroll Into View    ${SEL_RESULTS_TABLE}
       Evaluate    document.querySelector('${SEL_RESULTS_TABLE}').scrollTop = 180
       Capture Step    caption=Scroll through the observation list    delay=2500

       Export Demo
       ...    mast-jwst-search
       ...    out_dir=${CURDIR}/../../examples/wireframes
       ...    rst=True

.. note::

   The selectors above target the Vuetify components used in the MAST SPA at
   the time of writing.  If the MAST UI changes, inspect the live page with
   browser DevTools and update the ``${SEL_*}`` variables.  The ``Route API``
   pattern ``**/api/v0.1/missions/search**`` must match the URL the Vue app
   calls when the Search button is clicked — verify in the DevTools Network
   tab.

Mock data format
~~~~~~~~~~~~~~~~

The ``body_file`` argument points to a JSON file whose content is the
**complete response body** that the application would receive from the real
API.  The structure must match whatever the application code expects from
``response.json()`` — inspect the real API with DevTools and replicate the
envelope exactly.

For the MAST search API the envelope looks like:

.. code-block:: json

   {
     "status": "COMPLETE",
     "paging": {"page": 1, "pageSize": 25, "rows": 10, ...},
     "fields": [{"name": "obs_id", "type": "string"}, ...],
     "data": [
       {"obs_id": "jw01783001001_02101_00001_nrcb1",
        "target_name": "NGC-1300",
        "instrument_name": "NIRCAM",
        "filters": "F200W",
        "t_exptime": 1289.674,
        ...},
       ...
     ]
   }

A complete 10-row fixture for NGC 1300 JWST observations is provided in
``examples/rf/mast-jwst-mock.json``.


Running the capture
--------------------

.. code-block:: bash

   # Basic run — output goes to same dir as the .robot file
   guidestar-capture examples/rf/mast-jwst-search.robot

   # Specify output dir and generate a Sphinx RST snippet
   guidestar-capture examples/rf/mast-jwst-search.robot \
       --out examples/wireframes \
       --rst

   # DOM mode with a standalone self-contained HTML page
   guidestar-capture examples/rf/mast-jwst-search.robot \
       --mode dom \
       --out examples/wireframes \
       --standalone

   # Override viewport and height without editing the .robot file
   guidestar-capture examples/rf/mast-jwst-search.robot \
       --viewport 1280 --height 600px \
       --out /tmp/test-capture

The command writes to the output directory:

.. code-block:: text

   examples/wireframes/
     mast-jwst-search.html      ← wireframe HTML (screenshot or DOM)
     mast-jwst-search.json      ← Guidestar demo config
     mast-jwst-search.rst       ← Sphinx directive snippet (if --rst)
     mast-jwst-search-standalone.html  ← self-contained page (if --standalone)
     _capture_output/           ← Robot Framework logs (log.html, report.html)

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

.. code-block:: json

   {
     "wireframe": "mast-jwst-search.html",
     "title": "Mast Jwst Search",
     "height": "720px",
     "viewport": 1440,
     "repeat": true,
     "steps": [
       {
         "actions": [
           {"target": "#gs-capture-root", "action": "remove-class", "value": "gs-slide-active-0"},
           {"target": "#gs-capture-root", "action": "add-class",    "value": "gs-slide-active-1"}
         ],
         "delay": 2200,
         "caption": "Enter a target name or sky coordinates"
       },
       ...
     ]
   }

This config is compatible with ``guidestar-build`` unchanged — no new
actions, no controller changes.

Embedding in docs
~~~~~~~~~~~~~~~~~

If you ran with ``--rst``, a ``.rst`` snippet is written alongside the
wireframe.  Copy it into your RST file:

.. code-block:: rst

   .. guidestar-demo:: _static/mast-jwst-search.html
      :height: 720px
      :viewport: 1440
      :steps-json: [{"actions": [...]}, ...]
      :repeat: true

Or use the generated ``{name}-standalone.html`` (``--standalone``) in an
iframe:

.. code-block:: rst

   .. raw:: html

      <iframe src="https://yourorg.github.io/yourrepo/demos/mast-jwst-search-standalone.html"
              style="width:100%;height:720px;border:none;display:block"
              loading="lazy" title="MAST JWST Search Demo"></iframe>


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
       guidestar-capture examples/rf/mast-jwst-search.robot \
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
