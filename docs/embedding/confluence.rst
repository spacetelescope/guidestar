Confluence
==========

Guidestar demos can be embedded in Confluence pages in three ways: as
**animated GIFs** (works everywhere, no JavaScript required), as
**interactive HTML pages** embedded via iframe (works on platforms that
permit JavaScript in iframes, such as when using the Bobswift HTML macro),
or as a **Bobswift-hosted interactive demo** where only the wireframe is
hosted externally and the step definitions live directly in the macro body.

.. note::

   Confluence's built-in iframe macro uses ``sandbox="sandbox"`` which blocks
   all JavaScript execution.  For this reason, interactive HTML embeds do not
   work via Confluence's native iframe macro.  The options described below
   work around this limitation.


Embedding in Confluence with Bobswift
-------------------------------------

1. Install the `Bobswift HTML macro
   <https://marketplace.atlassian.com/apps/1210-html-macro>`_ from the
   Atlassian Marketplace (requires Confluence admin access).

2. On the Confluence page, insert the **HTML macro** (leave all options as default) 
   and paste one of the options described below into the macro body.

3. Adjust ``height`` to match the ``height`` set in the demo
   :ref:`config JSON <json-object-format>`
   (add ~40 px for the page chrome).

The demo loads with full play/pause/restart controls and auto-starts when
scrolled into view.

.. guidestar-demo:: _static/confluence-bobswift.html
   :steps: #search-input@1000:click|Click "Search macros", #search-input@2200:type-text=bobswift|Type "bobswift", #app@500:add-class=searched, #bobswift-result@1500:click|^Click Html-bobswift, #app@400:add-class=inserting, #insert-btn@1800:click|Click Insert, #app@400:add-class=inserted, pause@700, #macro-content@5000:type-text=<pasted code from sections below>|^Paste the iframe embed code, pause@2000
   :height: 580px
   :viewport: 860
   :repeat: true


Embed with Demo Defined Inline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Four sub-approaches are available depending on where your wireframe
HTML lives:

**Wireframe hosted externally (GitHub Pages, S3, etc.)**
   Use ``htmlSrc`` pointing to the wireframe URL.  The host must return
   permissive CORS headers; GitHub Pages does this by default.

   .. code-block:: html

      <div id="gs-demo" style="width:100%;height:420px"></div>
      <link rel="stylesheet"
            href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">
      <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>
      <script>
        new Guidestar(document.getElementById('gs-demo'), {
          htmlSrc: 'https://spacetelescope.github.io/guidestar/wireframes/kitchen-sink.html',
          steps: [
            '#btn-sidebar@1800:click|Open the sidebar',
            '#sidebar@800:toggle-class=open',
            '#input-search@1500:type-text=pipeline|Search for a pipeline',
            '#btn-action@1500:click|^Run the batch action',
            'pause@2000',
            '#sidebar@1200:toggle-class=open|vClose the sidebar',
            'pause@2000'
          ],
          height: 420,
          repeat: true
        });
      </script>

**Wireframe defined in an earlier macro on the same Confluence page**
   Give the wireframe container an ``id`` (or any unique selector) in the
   earlier macro, then use ``htmlSrcSelector`` in the demo macro.  The
   controller clones that element from the live page DOM — no fetch required.

   *Earlier macro on the page (wireframe only):*

   .. code-block:: html

      <div id="my-wireframe" style="display:none">
        <!-- wireframe HTML here -->
      </div>

   *Demo macro (steps defined here, wireframe cloned from above):*

   .. code-block:: html

      <div id="gs-demo" style="width:100%;height:420px"></div>
      <link rel="stylesheet"
            href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">
      <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>
      <script>
        new Guidestar(document.getElementById('gs-demo'), {
          htmlSrcSelector: '#my-wireframe',
          steps: [
            '#btn-sidebar@1800:click|Open the sidebar',
            '#sidebar@800:toggle-class=open',
            'pause@2000'
          ],
          height: 420,
          repeat: true
        });
      </script>

**Wireframe defined in a macro on a different Confluence page**
   If the other page is same-origin (or publicly accessible), use ``htmlSrc``
   **and** ``htmlSrcSelector`` together.  The controller fetches the remote
   URL, parses it, and extracts only the matching element as the wireframe.

   .. code-block:: html

      <div id="gs-demo" style="width:100%;height:420px"></div>
      <link rel="stylesheet"
            href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">
      <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>
      <script>
        new Guidestar(document.getElementById('gs-demo'), {
          htmlSrc: 'https://your-confluence.example.com/wiki/spaces/TEAM/pages/123456/Wireframe+Library',
          htmlSrcSelector: '#my-wireframe',
          steps: [
            '#btn-sidebar@1800:click|Open the sidebar',
            '#sidebar@800:toggle-class=open',
            'pause@2000'
          ],
          height: 420,
          repeat: true
        });
      </script>

**Wireframe defined in the same macro**
   Place the wireframe HTML as children of the ``[data-guidestar]`` container
   and omit both ``htmlSrc`` and ``htmlSrcSelector``.  No network request is
   made; no CORS configuration is needed.

   .. code-block:: html

      <link rel="stylesheet"
            href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">
      <div id="gs-demo" style="width:100%;height:120px"
           data-guidestar
           data-guidestar-config='{
             "steps": [
               "#my-btn@1500:click|Click the button",
               "#my-panel@1000:toggle-class=open|Toggle the panel",
               "pause@2000"
             ],
             "repeat": true
           }'>
        <!-- inline wireframe HTML -->
        <style>
          #my-panel { display: none; padding: 8px; background: #eef; }
          #my-panel.open { display: block; }
        </style>
        <button id="my-btn">Click me</button>
        <div id="my-panel">Panel content</div>
      </div>
      <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>


Demo Defined and Hosted from GitHub Pages
-----------------------------------------

The :doc:`../gh_actions/deploy-demos` reusable workflow builds self-contained
HTML pages from your demo configs and deploys them to GitHub Pages.  See that
page for the full setup guide, but in brief — add this to your repo:

.. code-block:: yaml
   :caption: ``.github/workflows/deploy-demos.yml``

   jobs:
     deploy:
       permissions:
         contents: read
         pages: write
         id-token: write
       uses: spacetelescope/guidestar/.github/workflows/deploy-demos.yml@main
       with:
         demos-dir: guidestar-demos

Once deployed, each demo is available at a stable URL:

.. code-block:: text

   https://<org>.github.io/<repo>/kitchen-sink-full.html
   https://<org>.github.io/<repo>/mast-hst.html

Enable GitHub Pages in your repository **Settings → Pages** and set the
source to **GitHub Actions**.

When embedding from GitHub pages, the content in the Bobswift macro is an iframe embedding the
hosted demo page:

   .. code-block:: html

      <iframe
        src="https://<org>.github.io/<repo>/kitchen-sink-full.html"
        width="100%"
        height="460"
        frameborder="0"
        scrolling="no"
        allowfullscreen>
      </iframe>


Embed GIF Hosted by GitHub Pages
--------------------------------

Animated GIFs are the simplest embedding option and work in any Confluence
environment without any special macros or admin configuration.

For instructions on how to generate the GIF itself, see :doc:`recording`.


Setting up GitHub Pages for GIF hosting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pass ``record-gifs: true`` to the :doc:`../gh_actions/deploy-demos` workflow
and it will record GIFs alongside the HTML pages:

.. code-block:: yaml

       uses: spacetelescope/guidestar/.github/workflows/deploy-demos.yml@main
       with:
         demos-dir: guidestar-demos
         record-gifs: true

Once deployed, each GIF is available at:

.. code-block:: text

   https://<org>.github.io/<repo>/kitchen-sink-full.gif
   https://<org>.github.io/<repo>/mast-hst.gif


Embedding the GIF in Confluence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use Confluence's built-in **image macro** to embed the animated GIF by URL:

1. Get the GIF URL from GitHub Pages::

      https://<org>.github.io/<repo>/kitchen-sink-full.gif

2. In Confluence, insert an image by URL (or use the ``!`` image macro in
   wiki markup)::

      !https://<org>.github.io/<repo>/kitchen-sink-full.gif!

The GIF loops automatically and plays the full demo sequence without
requiring any JavaScript.

For example, the "kitchen-sink-short" demo GIF hosted on GitHub Pages:

.. image:: https://spacetelescope.github.io/guidestar/kitchen-sink-short.gif
   :alt: Kitchen Sink Short — animated GIF demo
   :width: 100%


Troubleshooting
---------------

**GIF does not appear in Confluence**
   Verify the GitHub Pages URL loads the GIF correctly in a new browser
   tab.  Check that GitHub Pages is enabled in the repo settings and that
   the ``pages.yml`` workflow has completed successfully.

**iFrame shows a blank page**
   Confirm that the Bobswift macro is installed and that the GitHub Pages
   URL is publicly accessible.  The demo page requires JavaScript — check
   the browser console for errors if the demo loads but does not play.
