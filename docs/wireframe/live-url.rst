Live URL
========

Instead of a static wireframe HTML file, you can point guidestar at a
**live URL** — any same-origin page that renders the real application.
This is useful when:

* your application is already deployed and you want demos that always
  reflect the current UI without maintaining a separate wireframe file;
* you are documenting a tool that lives on the same server as your docs
  (e.g. a GitHub Pages–hosted utility alongside your Sphinx site).

.. note::

   **Same-origin requirement.**  The browser's ``fetch()`` API enforces the
   `Same-Origin Policy`_.  A live URL will only load without extra
   configuration when the demo page and the target URL share the same
   origin (scheme + host + port).  Cross-origin URLs require the target
   server to send ``Access-Control-Allow-Origin`` CORS headers.

   GitHub Pages automatically serves permissive CORS headers for all
   files, so any two pages under the same GitHub Pages site
   (e.g. ``https://yourorg.github.io/yourrepo/``) are same-origin
   and load without restriction.

.. _Same-Origin Policy: https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy


How it works
------------

The ``htmlSrc`` option accepts any URL.  At page-load time guidestar calls
``fetch(htmlSrc)``, parses the response as HTML, scopes the wireframe's
styles via CSS ``@scope`` to prevent leakage into the host page (see
:ref:`css-isolation`), and injects the body content into the demo
container.  From that point the demo behaves identically to one backed by
a static wireframe file.

.. code-block:: json

   {
     "htmlSrc": "https://spacetelescope.github.io/guidestar/demo-builder.html",
     "viewport": 1440,
     "initSteps": [
       {"target": "#recording-body", "action": "add-class", "value": "collapsed"},
       {"target": "#steps-body",     "action": "add-class", "value": "collapsed"}
     ],
     "steps": [
       {"target": "#source-url", "action": "highlight", "delay": 1200,
        "caption": "Enter the URL of your wireframe"}
     ]
   }

In RST:

.. code-block:: rst

   .. guidestar-demo:: https://spacetelescope.github.io/guidestar/demo-builder.html
      :viewport: 1440
      :steps-json: [{"target":"#source-url","action":"highlight","delay":1200}]


Embedding as an iframe (recommended for docs)
---------------------------------------------

When multiple demos on a single docs page each load a heavy live URL, the
page would make many ``fetch()`` requests and inject the full application
DOM multiple times.  A lighter pattern is to:

1. Create one self-contained demo HTML file per step (containing the
   ``data-guidestar-config`` and the two asset tags).
2. Deploy those files alongside your application on the same server.
3. Embed them in RST using ``.. raw:: html`` ``<iframe>`` tags.

This is the same approach used for :doc:`../embedding/confluence` embeds.

Example file (``demos/web-tool/step-1.html``):

.. code-block:: html

   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <link rel="stylesheet" href="../../guidestar-controls.css">
     <style>html,body{margin:0;padding:0;background:transparent}</style>
   </head>
   <body>
   <div style="width:100%;height:320px"
        data-guidestar
        data-guidestar-config='{
          "htmlSrc": "../../demo-builder.html",
          "viewport": 1440,
          "repeat": true,
          "initSteps": [
            {"target":"#recording-body","action":"add-class","value":"collapsed"},
            {"target":"#steps-body","action":"add-class","value":"collapsed"}
          ],
          "steps": [
            {"target":"#source-url","action":"highlight","delay":1200,
             "caption":"Enter the URL of your wireframe"}
          ]
        }'></div>
   <script src="../../guidestar-controller.js"></script>
   </body>
   </html>

RST embed:

.. code-block:: rst

   .. raw:: html

      <iframe src="https://yourorg.github.io/yourrepo/demos/step-1.html"
              style="width:100%;height:320px;border:none;display:block"
              loading="lazy" title="Demo: Load a source"></iframe>

The ``loading="lazy"`` attribute defers fetching until the iframe scrolls
into view, keeping the initial page-load fast.


Preventing user interaction with the source
--------------------------------------------

When using a live URL, the injected page is fully functional — buttons,
links, accordions, and forms all work.  For demo purposes you almost
always want to **prevent** viewers from interacting with the content so
they don't accidentally navigate away, collapse a section mid-step, or
submit a form.

Guidestar's ``allowUserInteractions`` option (default: ``false``) places
a transparent glass pane over the demo content.  All clicks on the
content area toggle play/pause instead of reaching the underlying page.
The playback controls, timeline, and fullscreen button are above the pane
and always usable.

.. code-block:: json

   {
     "htmlSrc": "https://example.com/app.html",
     "allowUserInteractions": false
   }

In RST (the default — you don't need to specify it explicitly):

.. code-block:: rst

   .. guidestar-demo:: https://example.com/app.html

To **allow** interaction (e.g. you want viewers to try the UI themselves
while the demo is paused):

.. code-block:: rst

   .. guidestar-demo:: https://example.com/app.html
      :allow-user-interactions: true
      :pause-on-interaction: true

.. note::

   ``:pause-on-interaction:`` only takes effect when
   ``:allow-user-interactions: true``.  With the default ``false``, all
   content-area clicks are handled by the interaction blocker and
   ``:pause-on-interaction:`` is ignored.

For live URL sources, **always leave** ``allowUserInteractions`` at its
default (``false``).  A viewer clicking a link in the embedded live page
could navigate the live application to an unexpected state with no way to
undo it short of a full reload.

.. note::

   With ``allowUserInteractions: false``, the overlay that intercepts
   clicks also prevents text selection inside the demo.  Viewers cannot
   copy text, URLs, or code snippets shown in the content.  If your demo
   contains copyable text (e.g. a command shown in a terminal pane), set
   ``allowUserInteractions: true`` — but only when using a static wireframe
   where there is no risk of real navigation.  Never set it to ``true`` for
   live-URL sources.


Restart and timeline seek behaviour
-------------------------------------

By default, guidestar restores the demo to its initial state by setting
``_contentRoot.innerHTML`` back to a snapshot taken after the first
``fetch()`` and re-executing any inline ``<script>`` tags.  For static
wireframes this is perfectly reliable.

For live application pages it can fall short in two ways:

* **Stacking global listeners** — scripts that call
  ``document.addEventListener(...)`` or attach listeners to elements
  outside the content container accumulate a new handler on every restart.
* **Stale closures** — if a script captures a reference to a DOM node at
  initialization time (e.g. ``var btn = document.getElementById('btn')``
  at the top level), that reference points to the original node, not the
  one re-inserted after an ``innerHTML`` reset.

For most demo use cases (``highlight``, ``add-class``, ``set-text`` steps
that don't depend on JS interactivity inside the wireframe) this doesn't
matter at all.  If you need the live application to be fully interactive
after each restart — or if the application's init logic breaks on re-run —
use ``reloadOnRestart``.


``reloadOnRestart``
~~~~~~~~~~~~~~~~~~~~

Setting ``reloadOnRestart: true`` changes the restart and loop behavior: on
every restart guidestar re-fetches the original ``htmlSrc`` URL and
re-initialises the content from scratch, including re-running ``initSteps``.
This guarantees a clean initial DOM state every cycle.

.. code-block:: json

   {
     "htmlSrc": "https://spacetelescope.github.io/guidestar/demo-builder.html",
     "reloadOnRestart": true,
     "initSteps": [
       {"target": "#recording-body", "action": "add-class", "value": "collapsed"}
     ],
     "steps": [
       {"target": "#source-url", "action": "highlight", "delay": 1200}
     ]
   }

In RST:

.. code-block:: rst

   .. guidestar-demo:: https://example.com/app.html
      :reload-on-restart: true
      :steps: #source-url@1200:highlight

**Tradeoffs:**

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Behaviour
     - Default (innerHTML reset)
     - ``reloadOnRestart: true``
   * - Restart speed
     - Instant
     - One network round-trip
   * - Event listeners re-bound
     - Only those in inline ``<script>`` tags
     - All, exactly as on first load
   * - Works with ``repeat: true``
     - Yes
     - Yes (re-fetches on every loop)
   * - Works offline / ``file://``
     - Yes
     - No (requires ``fetch()``)
   * - Timeline seek (click a dot)
     - Uses ``_htmlSnapshots`` / ``_initialHTML``
     - Still uses snapshot; only *full restart* re-fetches

.. note::

   With ``repeat: true`` and ``reloadOnRestart: true`` the source URL is
   re-fetched on every loop end, so the page always restarts from a clean
   state. On a slow connection this adds a visible loading pause between
   repetitions; consider setting ``repeat: false`` and letting users click
   the restart button manually.



A live application renders its real initial DOM state, which may differ
from what you want to show in a demo.  Use ``initSteps`` to collapse
sections you don't want to highlight and open the one you do.  ``initSteps``
run instantly before playback starts with no animation or delay, so viewers
never see the reset happening.

For example, to show only the "Output" section of the Demo Builder:

.. code-block:: json

   "initSteps": [
     {"target": "#source-body",    "action": "add-class",    "value": "collapsed"},
     {"target": "#recording-body", "action": "add-class",    "value": "collapsed"},
     {"target": "#steps-body",     "action": "add-class",    "value": "collapsed"},
     {"target": "#output-body",    "action": "remove-class", "value": "collapsed"},
     {"target": "#section-output .card-header",
                                   "action": "remove-class", "value": "collapsed"}
   ]


Limitations
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Limitation
     - Notes
   * - **Same-origin only** (without CORS)
     - The target URL must be on the same origin as the page embedding the
       demo, or the server must send ``Access-Control-Allow-Origin`` headers.
       GitHub Pages returns ``*`` by default.
   * - **No offline / file:// support**
     - Unlike a static wireframe, a live URL cannot be previewed from a
       local ``file://`` path.  You need a local server.
   * - **Scripts re-run imperfectly on restart**
     - Guidestar re-injects ``<script>`` tags via ``_runScripts()`` but
       global ``document.addEventListener`` calls stack on each restart
       and closures that captured the original DOM nodes may be stale.
       For ``highlight`` / ``add-class`` style demos this is harmless.
       For demos that need full JS interactivity after restart, use
       ``reloadOnRestart: true`` — see `Restart and timeline seek behaviour`_.
   * - **External stylesheets not scoped**
     - Guidestar scopes inline ``<style>`` blocks via CSS ``@scope`` but
       cannot scope ``<link rel="stylesheet">`` external sheets.  If the
       live URL links to a global stylesheet, those rules apply to the whole
       host page.  Prefer inline styles, or use a static wireframe.
   * - **GIF snapshots not supported**
     - ``guidestar-record`` opens built demo pages via ``file://`` and reads
       step timing from a companion JSON config file.  Live-URL demos have
       neither: the inner ``fetch()`` fails under ``file://``, and there is
       no JSON config for the recorder to extract timing from.  As a result
       ``guidestar-record`` silently skips any demo that uses a live URL.
       To produce a GIF, record a static wireframe that mirrors the same UI
       instead, or add a JSON config and update the recorder to serve pages
       via a local HTTP server.
   * - **No sync guarantee**
     - There is no built-in mechanism to detect when the live page has
       changed in a way that breaks recorded step selectors.  Consider
       running the :doc:`../gh_actions/wireframe-review` action targeting
       the demo HTML files to catch broken selectors in CI.
