Quick Start
===========

Installation
------------

Install from source (or from PyPI once published):

.. code-block:: bash

   pip install guidestar

For building documentation locally you will also need the theme:

.. code-block:: bash

   pip install guidestar[docs]


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


Live example
------------

.. guidestar-demo:: _static/example-wireframe.html
   :steps: #demo-btn-1@1500:click|Click the first button, #demo-panel@1000:toggle-class=open|^Toggle the panel open, #demo-btn-2@1500:add-class=active|Activate the second button, #demo-input@1500:type-text=Hello World|Type into the input, #demo-btn-2@1500:remove-class=active, #demo-panel@1000:toggle-class=open|vClose the panel
   :height: 300px
   :repeat: true


Minimal standalone HTML example
-------------------------------

No Sphinx needed — just include the JS and CSS files directly:

.. code-block:: html

   <!DOCTYPE html>
   <html>
   <head>
       <link rel="stylesheet" href="guidestar-controls.css">
   </head>
   <body>
       <div data-guidestar
            data-guidestar-config='{
              "htmlSrc": "my-app.html",
              "steps": [
                {"target": "#btn", "action": "click", "delay": 1500, "caption": "Click the button"},
                {"target": "#panel", "action": "toggle-class", "value": "open", "delay": 1000, "caption": "Open the panel", "captionOptions": {"position": "bottom"}}
              ]
            }'>
       </div>
       <script src="guidestar-controller.js"></script>
   </body>
   </html>
