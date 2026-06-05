Deploy Demos to GitHub Pages
============================

The ``deploy-demos`` reusable workflow builds self-contained interactive HTML
pages (and optionally animated GIFs) from your guidestar demo configs and
deploys them to GitHub Pages.  Any repository can call it with a single
workflow file — no build scripts or asset management required.

.. note::

   Demos are always deployed to the **root** of your GitHub Pages site
   (``https://<org>.github.io/<repo>/``).  Subfolder deployment is not
   currently supported.


Prerequisites
-------------

1. In your repository go to **Settings → Pages** and set the source to
   **GitHub Actions**.

2. Create a ``guidestar-demos/`` directory (or any name you choose) in the
   repository root with the following layout:

   .. code-block:: text

      guidestar-demos/
        my-app.json            # demo config file
        another-demo.json      # one file per demo
        wireframes/
          my-app.html          # wireframe HTML for my-app
          another-demo.html

   The ``wireframe`` field in each JSON config must match a filename inside
   the ``wireframes/`` subdirectory.  See :doc:`../demos/configuration`
   for the full list of config fields.


Calling the Workflow
--------------------

Create ``.github/workflows/deploy-demos.yml`` in your repository:

.. code-block:: yaml
   :caption: ``.github/workflows/deploy-demos.yml`` (minimal)

   name: Deploy Demos

   on:
     push:
       branches: [main]
       paths:
         - 'guidestar-demos/**'
     workflow_dispatch:

   jobs:
     deploy:
       permissions:
         contents: read
         pages: write
         id-token: write
       uses: spacetelescope/guidestar/.github/workflows/deploy-demos.yml@main
       with:
         demos-dir: guidestar-demos

On every push to ``main`` that touches the ``guidestar-demos/`` directory,
the workflow will build the interactive HTML pages and publish them to
GitHub Pages.


.. _deploy-demos-inputs:

Inputs Reference
----------------

.. list-table::
   :header-rows: 1
   :widths: 22 12 66

   * - Input
     - Default
     - Description
   * - ``demos-dir``
     - ``guidestar-demos``
     - Directory containing ``*.json`` demo config files.
   * - ``wireframes-dir``
     - *(empty)*
     - Directory containing wireframe HTML files.  Defaults to
       ``<demos-dir>/wireframes`` when left empty.
   * - ``record-gifs``
     - ``false``
     - Also record animated GIF versions of each demo.  Adds Playwright +
       Chromium install time to the run.
   * - ``fps``
     - ``10``
     - GIF frame rate (frames per second).  Only used when
       ``record-gifs: true``.
   * - ``width``
     - ``800``
     - Viewport width in pixels used when recording GIFs.
   * - ``index-title``
     - ``Wireframe Demos``
     - Title shown on the auto-generated ``index.html`` landing page.
   * - ``guidestar-version``
     - *(empty)*
     - pip version specifier for ``sphinx-guidestar``, e.g. ``0.2.0``.
       Leave empty to use the latest published release.
   * - ``python-version``
     - ``3.11``
     - Python version used to run the build.


Demo Config Format
------------------

Each JSON file in ``demos-dir`` describes one demo.  The ``wireframe`` field
is required; all others are optional.

.. code-block:: json

   {
     "wireframe": "my-app.html",
     "title": "My App — Feature Tour",
     "height": "480px",
     "steps": [
       "#sidebar-toggle@1200:click|Open the sidebar",
       "#search-input@1500:type-text=hello world|Type a query",
       "#search-btn@1000:click|Submit the search"
     ],
     "repeat": true,
     "autoStart": true
   }

The ``steps`` array accepts the same shorthand strings or
:ref:`JSON object format <json-object-format>` as the
Sphinx directive's ``:steps:`` option — see :doc:`../demos/configuration` for
the complete step syntax and all available config fields.


Examples
--------

Interactive HTML only (fastest)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml
   :caption: ``.github/workflows/deploy-demos.yml``

   name: Deploy Demos
   on:
     push:
       branches: [main]
       paths: ['guidestar-demos/**']
     workflow_dispatch:
   jobs:
     deploy:
       permissions:
         contents: read
         pages: write
         id-token: write
       uses: spacetelescope/guidestar/.github/workflows/deploy-demos.yml@main
       with:
         demos-dir: guidestar-demos
         index-title: My Project Demos

Once deployed, each demo is accessible at:

.. code-block:: text

   https://<org>.github.io/<repo>/my-app.html
   https://<org>.github.io/<repo>/another-demo.html
   https://<org>.github.io/<repo>/             ← auto-generated index


Interactive HTML + GIF recording
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml
   :caption: ``.github/workflows/deploy-demos.yml``

   name: Deploy Demos
   on:
     push:
       branches: [main]
       paths: ['guidestar-demos/**']
     workflow_dispatch:
   jobs:
     deploy:
       permissions:
         contents: read
         pages: write
         id-token: write
       uses: spacetelescope/guidestar/.github/workflows/deploy-demos.yml@main
       with:
         demos-dir: guidestar-demos
         record-gifs: true
         fps: 12
         width: 1024

Each demo is built as both an interactive HTML page and an animated GIF:

.. code-block:: text

   https://<org>.github.io/<repo>/my-app.html
   https://<org>.github.io/<repo>/my-app.gif


Custom wireframes directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your wireframes live in a separate directory from the JSON configs:

.. code-block:: yaml

       uses: spacetelescope/guidestar/.github/workflows/deploy-demos.yml@main
       with:
         demos-dir: docs/demos
         wireframes-dir: docs/wireframes


Pin to a specific guidestar release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

       uses: spacetelescope/guidestar/.github/workflows/deploy-demos.yml@main
       with:
         demos-dir: guidestar-demos
         guidestar-version: '0.2.0'
