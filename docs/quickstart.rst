Quick Start
===========

Installation
------------

Install from source (or from PyPI once published):

.. code-block:: bash

   pip install sphinx-guidestar

For building documentation locally you will also need the theme:

.. code-block:: bash

   pip install sphinx-guidestar[docs]


Minimal Sphinx example
----------------------

1. Add the extension to your Sphinx ``conf.py``:

   .. code-block:: python

      extensions = [
          'guidestar',
      ]

2. Place your wireframe HTML in ``docs/_static/my-app.html``.

3. Use the directive in any RST file:

   .. code-block:: rst

      .. guidestar-demo:: _static/my-app.html
         :steps: #start-btn@1500:click, #panel@1000:toggle-class=open, #save-btn@2000:click
         :height: 400px

   This will:

   * Fetch ``my-app.html`` at page load
   * Inject it into a container with play/pause/restart controls
   * Step through the actions, highlighting each target element
   * Pause if the user clicks anywhere inside the demo


.. guidestar-demo:: _static/example-wireframe.html
   :steps: #demo-btn-1@1500:click|Click the first button, #demo-panel@1000:toggle-class=open|^Toggle the panel open, #demo-btn-2@1500:add-class=active|Activate the second button, #demo-input@1500:type-text=Hello World|Type into the input, #demo-btn-2@1500:remove-class=active, #demo-panel@1000:toggle-class=open|vClose the panel
   :height: 300px
   :repeat: true


4. To show a **static snapshot** instead — no controls, just the wireframe
   frozen at a specific state — omit ``:steps:`` and use ``:init-steps-json:``
   to set up the scene:

   .. code-block:: rst

      .. guidestar-demo:: _static/my-app.html
         :init-steps-json:
            [
              {"target": "#panel", "action": "add-class", "value": "open"},
              {"target": "#action-btn", "action": "add-class", "value": "active",
               "caption": "Click Action to run the pipeline",
               "captionOptions": {"position": "bottom"}}
            ]
         :height: 400px

   This will:

   * Fetch ``my-app.html`` and silently apply the init steps (open the panel,
     activate the button)
   * Render the wireframe frozen at that state — no play/pause controls
   * Show the cursor resting on ``#action-btn`` (the last targeted init step)
   * Display the caption as a persistent overlay

   Set ``:cursor: false`` to hide the cursor if you want a clean screenshot-
   like embed with no cursor visible.

.. guidestar-demo:: _static/example-wireframe.html
   :init-steps-json:
      [
        {"target": "#demo-panel", "action": "add-class", "value": "open"},
        {"target": "#demo-btn-2", "action": "add-class", "value": "active",
         "caption": "Click Action to run the pipeline",
         "captionOptions": {"position": "bottom"}}
      ]
   :height: 300px





Minimal standalone HTML example
-------------------------------

No Sphinx needed — just include the JS and CSS files directly.  The example
below uses the controller and wireframe hosted on GitHub Pages so it works
without any local files:

.. code-block:: html

   <!DOCTYPE html>
   <html>
   <head>
       <link rel="stylesheet"
             href="https://spacetelescope.github.io/guidestar/guidestar-controls.css">
   </head>
   <body>
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
            }'>
       </div>
       <script src="https://spacetelescope.github.io/guidestar/guidestar-controller.js"></script>
   </body>
   </html>

Result:

.. guidestar-demo:: https://spacetelescope.github.io/guidestar/wireframes/kitchen-sink.html
   :steps: #btn-sidebar@1800:click|Open the sidebar, #sidebar@800:toggle-class=open, #input-search@1500:type-text=pipeline|Search for a pipeline, #btn-action@1500:click|^Run the batch action, pause@2000, #sidebar@1200:toggle-class=open|vClose the sidebar, pause@2000
   :height: 420px
   :repeat: true
