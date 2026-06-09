.. _html-embedding:

Standalone HTML
===============

You can use guidestar in any HTML page without Sphinx.
Just include the two asset files and set up your containers.

.. note::

   For a full list of configuration parameters, their types, defaults, and
   descriptions, see the :doc:`../demos/configuration`.


Include the assets
------------------

Copy (or serve) these two files from the package's ``static/`` directory:

* ``guidestar-controller.js``
* ``guidestar-controls.css``

They are also available directly from the Guidestar GitHub Pages site if you
want to load them without self-hosting:

.. code-block:: text

   https://spacetelescope.github.io/guidestar/guidestar-controller.js
   https://spacetelescope.github.io/guidestar/guidestar-controls.css

.. code-block:: html

   <link rel="stylesheet" href="guidestar-controls.css">
   <script src="guidestar-controller.js"></script>


Declarative usage
-----------------

Add a ``data-guidestar`` attribute and a ``data-guidestar-config``
JSON attribute to any element:

.. code-block:: html

   <link rel="stylesheet" href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">

   <div style="width:100%;height:420px"
        data-guidestar
        data-guidestar-config='{
     "htmlSrc": "https://spacetelescope.github.io/guidestar/wireframes/kitchen-sink.html",
     "steps": [
       "#btn-sidebar@1800:click|Open the sidebar",
       "#sidebar@800:toggle-class=open",
       "#input-search@1500:type-text=pipeline|Search for a pipeline",
       "#btn-action@1500:click|^Run the batch action",
       "pause@2000",
       "#sidebar@1200:toggle-class=open|vClose the sidebar",
       "pause@2000"
     ],
     "repeat": true
   }'></div>

   <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>

The controller auto-discovers these elements on ``DOMContentLoaded``.


Wireframe content sources
--------------------------

Guidestar supports four ways to provide the wireframe HTML, controlled by
``htmlSrc`` and ``htmlSrcSelector``:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - ``htmlSrc``
     - ``htmlSrcSelector``
     - Behaviour
   * - provided
     - omitted
     - Fetches the URL and uses the full response body as the wireframe.
   * - provided
     - provided
     - Fetches the URL, parses the response with ``DOMParser``, and extracts
       the first element matching the selector as the wireframe.
   * - omitted
     - provided
     - Clones the first element matching the selector from the **current page**
       DOM — no network request needed.
   * - omitted
     - omitted
     - Uses any HTML that already exists as children of the container element
       (inline wireframe).  Logs an error if the container is empty.


**Inline wireframe** (no fetch, no external file):

.. code-block:: html

   <link rel="stylesheet" href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">

   <div style="width:100%;height:420px"
        data-guidestar
        data-guidestar-config='{"steps":["#btn@1500:click|Click the button"],"repeat":true}'>
     <!-- wireframe HTML pasted directly here -->
     <button id="btn">Click me</button>
   </div>

   <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>


**Clone from an element already on the page** (e.g. a hidden template div):

.. code-block:: html

   <!-- Wireframe lives elsewhere on the page -->
   <div id="my-wireframe" style="display:none">
     <button id="btn">Click me</button>
   </div>

   <link rel="stylesheet" href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">

   <div style="width:100%;height:420px"
        data-guidestar
        data-guidestar-config='{
     "htmlSrcSelector": "#my-wireframe",
     "steps": ["#btn@1500:click|Click the button"],
     "repeat": true
   }'></div>

   <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>


**Extract a specific element from a remote URL**:

.. code-block:: html

   <link rel="stylesheet" href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">

   <div style="width:100%;height:420px"
        data-guidestar
        data-guidestar-config='{
     "htmlSrc": "https://example.com/page-with-wireframe.html",
     "htmlSrcSelector": "#wireframe-container",
     "steps": ["#btn@1500:click|Click the button"],
     "repeat": true
   }'></div>

   <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>


Programmatic usage
------------------

.. code-block:: html

   <link rel="stylesheet" href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">

   <div id="my-demo" style="width:100%;height:420px"></div>

   <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>
   <script>
   var demo = new Guidestar(document.getElementById('my-demo'), {
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
       repeat: true,
       onStepStart: function(index, step) {
           console.log('Step', index, step.action);
       }
   });

   // Control programmatically:
   // demo.pause();
   // demo.play();
   // demo.restart();
   // demo.destroy();
   </script>


Dynamically loaded HTML
-----------------------

If your wireframe HTML is loaded after the page (e.g. via a framework
router), dispatch the ``guidestar-loaded`` event to trigger
auto-discovery of any new containers:

.. code-block:: javascript

   // After injecting new guidestar containers into the DOM:
   document.dispatchEvent(new CustomEvent('guidestar-loaded'));


Full standalone example
-----------------------

.. code-block:: html

   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <title>Wireframe Demo — Standalone</title>
       <link rel="stylesheet" href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">
       <style>
           body { font-family: sans-serif; max-width: 800px; margin: 40px auto; }
           #demo-container { width: 100%; height: 420px; border: 1px solid #ccc; border-radius: 8px; }
       </style>
   </head>
   <body>
       <h1>My Application Demo</h1>
       <div id="demo-container"
            data-guidestar
            data-guidestar-config='{
              "htmlSrc": "https://spacetelescope.github.io/guidestar/wireframes/kitchen-sink.html",
              "steps": [
                "#btn-sidebar@1800:click|Open the sidebar",
                "#sidebar@800:toggle-class=open",
                "#input-search@1500:type-text=pipeline|Search for a pipeline",
                "#btn-action@1500:click|^Run the batch action",
                "pause@2000",
                "#sidebar@1200:toggle-class=open|vClose the sidebar",
                "pause@2000"
              ],
              "repeat": true
            }'>
       </div>
       <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>
   </body>
   </html>
