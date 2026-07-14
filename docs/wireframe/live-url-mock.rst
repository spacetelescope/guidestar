.. _live-url-mock:

Mocking API Calls in Live-URL Demos
=====================================

When a demo loads a live application page via ``htmlSrc``, that page's
interactive elements are fully functional inside the container — including
buttons that call external APIs.  During a recorded demo that loops
automatically this creates two problems:

* **Repeated external requests.** Every playthrough hits the real server,
  consuming quota, introducing latency, and making the demo dependent on
  network availability and API uptime.
* **Non-deterministic results.** Search results or data returned from a live
  API can change between playthroughs, so captions that describe specific
  results may become incorrect over time.

The solution is to give the live page a **mock hook** — a small, opt-in code
path that the demo activates before playback begins.  When the mock is active,
the page's action handler uses fixture data instead of calling the API.  The
live page works normally when opened directly in a browser; only the demo
context activates the shortcut.

.. note::

   This pattern requires that the live page and the demo are served from the
   **same origin** (so that Guidestar's ``fetch(htmlSrc)`` call succeeds).
   For GitHub Pages sites, both pages can live in the same repository under
   the same ``https://yourorg.github.io/yourrepo/`` origin.
   See :doc:`live-url` for background on the same-origin requirement.


How it works
------------

The mechanism has three parts that work together.

**1 — The live page exposes a mock hook**

The page's API-calling function checks ``window.__guidestarMock`` before
making any network request.  If the global is set to an array of result
objects, the handler uses those instead:

.. code-block:: javascript

   function doSearch() {
     var q = input.value.trim();
     if (!q) return;

     // Demo mock hook — set by a "mock-api" initStep before playback begins.
     if (window.__guidestarMock) {
       renderResults(window.__guidestarMock);
       return;
     }

     // Real API call — only runs when the page is used standalone.
     fetch('https://api.example.com/search?q=' + encodeURIComponent(q))
       .then(function (r) { return r.json(); })
       .then(function (data) { renderResults(data.results); });
   }

The global is ``null`` or ``undefined`` by default, so the check is a no-op
when the page runs outside a demo.

**2 — The demo registers a** ``mock-api`` **custom action**

Guidestar's custom-action API lets you register named actions that can be
used in any ``steps`` or ``initSteps`` array.  Add the following script
**after** the controller ``<script>`` tag in your demo HTML:

.. code-block:: html

   <script src="guidestar-controller.js"></script>
   <script>
   Guidestar.registerAction('mock-api', function (step, el, contentRoot) {
     try {
       window.__guidestarMock = JSON.parse(step.value);
     } catch (e) {
       console.error('[Guidestar] mock-api: step value is not valid JSON', e);
     }
   });
   </script>

The action receives the step's ``value`` field as a JSON string, parses it
into an array, and stores it on ``window.__guidestarMock``.

.. tip::

   ``Guidestar.registerAction`` is safe to call immediately after the
   controller script loads.  The controller's ``autoDiscover()`` triggers an
   async ``fetch()`` of the live page, so the registration always completes
   before ``initSteps`` run.

**3 — An** ``initStep`` **installs the mock before playback begins**

The ``initSteps`` array runs synchronously after the live page is fetched and
its scripts are executed, but before the first animated step plays.  Put the
``mock-api`` action there:

.. code-block:: json

   {
     "htmlSrc": "live-app.html",
     "allowUserInteractions": false,
     "initSteps": [
       {
         "target": "#search-app",
         "action": "mock-api",
         "value": "[{\"title\":\"Cosmos\",\"author\":\"Carl Sagan\",\"year\":1980}]"
       }
     ],
     "steps": [
       {"target": "#search-input", "action": "type-text", "value": "space exploration", "delay": 2200},
       {"target": "#search-btn",   "action": "click",     "delay": 1800},
       {"target": "#results",      "action": "highlight", "delay": 3500}
     ]
   }

The ``target`` can be any element that exists in the live page — it is passed
to the action handler as ``el`` but the ``mock-api`` action ignores it and
operates directly on ``window``.  ``#search-app`` (the page's root wrapper)
is a convenient choice because it is always present.

On every automatic restart (``repeat: true``), ``initSteps`` re-execute,
so ``window.__guidestarMock`` is re-installed and the demo stays consistent
across loops.


Working example
---------------

The demo below loads a live book-search page (`live-app.html`_) that calls
the `Open Library API`_.  An ``initStep`` installs five fixture books via
``mock-api`` before the demo starts.  The search button click is intercepted
by the mock hook, so the results appear instantly and identically on every
playthrough — without touching the Open Library server.

.. _live-app.html: https://spacetelescope.github.io/guidestar/demos/mock-api/live-app.html
.. _Open Library API: https://openlibrary.org/developers/api

.. raw:: html

   <iframe
     src="https://spacetelescope.github.io/guidestar/demos/mock-api/demo.html"
     style="width:100%;height:460px;border:none;display:block"
     loading="lazy"
     title="Demo: mocked Open Library search"></iframe>

Open `live-app.html`_ directly in your browser to use the real API; reload
the iframe above to confirm the demo always returns the same five books.


Setting up the live page
------------------------

Design the live page the same way as any static wireframe (self-contained
HTML, all CSS in ``<style>`` blocks, no external stylesheets) with two
additions:

1. **A root wrapper element** with a stable ``id`` so ``initSteps`` can
   target it.
2. **The mock-hook check** at the top of every API-calling function.

.. code-block:: html
   :caption: Minimal live page skeleton

   <!DOCTYPE html>
   <html lang="en">
   <head>
   <meta charset="UTF-8">
   <style>
     /* All styles inline — no external sheets */
     body { font-family: system-ui, sans-serif; padding: 24px; }
     /* ... */
   </style>
   </head>
   <body>
   <div id="my-app">          <!-- stable root id for initSteps target -->
     <input id="q" type="text" placeholder="Search…">
     <button id="search-btn" type="button">Search</button>
     <div id="results"></div>
   </div>
   <script>
   (function () {
     var btn  = document.getElementById('search-btn');
     if (!btn) return;  // guard against double-injection

     function doSearch() {
       var q = (document.getElementById('q').value || '').trim();
       if (!q) return;

       // Mock hook — set by the demo's "mock-api" initStep
       if (window.__guidestarMock) {
         renderResults(window.__guidestarMock);
         return;
       }

       // Live path (not reached during demo playback)
       fetch('https://api.example.com/search?q=' + encodeURIComponent(q))
         .then(function (r) { return r.json(); })
         .then(function (d) { renderResults(d.results); });
     }

     function renderResults(items) {
       document.getElementById('results').innerHTML =
         items.map(function (i) { return '<p>' + i.title + '</p>'; }).join('');
     }

     btn.addEventListener('click', doSearch);
   }());
   </script>
   </body>
   </html>

The ``if (!btn) return;`` guard is important: Guidestar re-executes ``<script>``
tags after injecting the HTML, so the IIFE runs again on every restart.  The
guard prevents ``addEventListener`` from stacking on the same element across
reloads (or if two demos on the same page load the same page).


Full demo config (standalone HTML)
-----------------------------------

Deploy these two files in the same directory on your GitHub Pages site.
The demo HTML references ``live-app.html`` with a relative URL so no
hard-coded origin is required:

.. code-block:: html
   :caption: ``demos/my-feature/demo.html``

   <!DOCTYPE html>
   <html lang="en">
   <head>
   <meta charset="UTF-8">
   <link rel="stylesheet" href="../../guidestar-controls.css">
   <style>html,body{margin:0;padding:0;background:transparent}</style>
   </head>
   <body>

   <div style="width:100%;height:460px"
        data-guidestar
        data-guidestar-config='{
     "htmlSrc": "live-app.html",
     "allowUserInteractions": false,
     "repeat": true,
     "cursor": true,
     "timeline": true,
     "initSteps": [
       {
         "target": "#my-app",
         "action": "mock-api",
         "value": "[{\"title\":\"Result A\"},{\"title\":\"Result B\"}]"
       }
     ],
     "steps": [
       {"target":"#q",          "action":"type-text","value":"widgets","delay":2000},
       {"target":"#search-btn", "action":"click",    "delay":1500},
       {"target":"#results",    "action":"highlight","delay":3000,
        "caption":"Results from mock data — no API call was made"}
     ]
   }'></div>

   <script src="../../guidestar-controller.js"></script>
   <script>
   Guidestar.registerAction('mock-api', function (step, el, contentRoot) {
     try {
       window.__guidestarMock = JSON.parse(step.value);
     } catch (e) {
       console.error('[Guidestar] mock-api:', e);
     }
   });
   </script>

   </body>
   </html>

Embed it in your RST documentation with a ``.. raw:: html`` iframe:

.. code-block:: rst

   .. raw:: html

      <iframe
        src="https://yourorg.github.io/yourrepo/demos/my-feature/demo.html"
        style="width:100%;height:460px;border:none;display:block"
        loading="lazy"
        title="Demo: my feature"></iframe>


Using with the Sphinx directive
---------------------------------

If your docs and your live page are both served from the same GitHub Pages
origin, you can also use the ``.. guidestar-demo::`` directive directly
(no iframe needed).  Register the custom action via the ``:js:`` option:

.. code-block:: rst

   .. guidestar-demo:: https://yourorg.github.io/yourrepo/demos/my-feature/live-app.html
      :allow-user-interactions: false
      :repeat: true
      :js: _static/mock-api-action.js
      :init-steps-json: [{"target":"#my-app","action":"mock-api","value":"[{\"title\":\"Result A\"},{\"title\":\"Result B\"}]"}]
      :steps-json: [
        {"target":"#q",          "action":"type-text","value":"widgets","delay":2000},
        {"target":"#search-btn", "action":"click",    "delay":1500},
        {"target":"#results",    "action":"highlight","delay":3000}
      ]

Where ``docs/_static/mock-api-action.js`` contains:

.. code-block:: javascript
   :caption: ``docs/_static/mock-api-action.js``

   document.addEventListener('guidestar-ready', function () {
     Guidestar.registerAction('mock-api', function (step, el, contentRoot) {
       try {
         window.__guidestarMock = JSON.parse(step.value);
       } catch (e) {
         console.error('[Guidestar] mock-api:', e);
       }
     });
   });

.. note::

   The ``:js:`` file is injected as a ``<script>`` tag before the demo
   container in the Sphinx output.  Wrapping the registration in a
   ``guidestar-ready`` listener ensures the action is registered even if
   the controller hasn't finished loading yet.

   When both the docs and the live page are on the same GitHub Pages site
   (same origin), the directive approach avoids the extra ``<iframe>``
   boundary and gives you RST-native step editing.  If the live page is
   on a different origin, use the standalone HTML + ``<iframe>`` pattern
   shown above.


Design guidelines
-----------------

``window.__guidestarMock`` naming
   The ``__guidestarMock`` naming convention signals that this global is
   *only* for demo tooling.  Keep it in the double-underscore namespace to
   avoid collisions with application code.

One mock per page load
   ``window.__guidestarMock`` is a page-level global.  If you embed two
   demos that load the same live page on the same docs page, they share the
   global and the second demo's ``initStep`` will overwrite the first's.
   In practice this is not an issue because demos autoplay sequentially
   rather than simultaneously, and both share the same underlying live page.

Resetting the mock on standalone use
   If you want the live page to explicitly clear the mock when used
   standalone (e.g. in an integration test), add this to the page's
   initialisation:

   .. code-block:: javascript

      // Clear any leftover mock from a previous demo context
      if (window.location.search.indexOf('guidestar') === -1) {
        window.__guidestarMock = null;
      }

   Most pages can skip this — the check ``if (window.__guidestarMock)``
   is a no-op when the global is ``undefined``.
