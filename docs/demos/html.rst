Standalone HTML
===============

You can use guidestar in any HTML page without Sphinx.
Just include the two asset files and set up your containers.

.. note::

   For a full list of configuration parameters, their types, defaults, and
   descriptions, see the :doc:`configuration`.


Include the assets
------------------

Copy (or serve) these two files from the package's ``static/`` directory:

* ``guidestar-controller.js``
* ``guidestar-controls.css``

.. code-block:: html

   <link rel="stylesheet" href="guidestar-controls.css">
   <script src="guidestar-controller.js"></script>


Declarative usage
-----------------

Add a ``data-guidestar`` attribute and a ``data-guidestar-config``
JSON attribute to any element:

.. code-block:: html

   <div data-guidestar
        data-guidestar-config='{
     "htmlSrc": "my-wireframe.html",
     "steps": [
       {"target": "#btn", "action": "click", "delay": 1500},
       {"target": "#panel", "action": "toggle-class", "value": "open", "delay": 1000}
     ],
     "repeat": true
   }'></div>

The controller auto-discovers these elements on ``DOMContentLoaded``.


Programmatic usage
------------------

.. code-block:: html

   <div id="my-demo"></div>

   <script>
   var demo = new Guidestar(document.getElementById('my-demo'), {
       htmlSrc: 'my-wireframe.html',
       steps: [
           { target: '#btn', action: 'click', delay: 1500 },
           { target: '#panel', action: 'toggle-class', value: 'open', delay: 1000 }
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
       <link rel="stylesheet" href="guidestar-controls.css">
       <style>
           body { font-family: sans-serif; max-width: 800px; margin: 40px auto; }
           #demo-container { border: 1px solid #ccc; border-radius: 8px; }
       </style>
   </head>
   <body>
       <h1>My Application Demo</h1>
       <div id="demo-container"
            data-guidestar
            data-guidestar-config='{
              "htmlSrc": "my-app-wireframe.html",
              "steps": [
                "#start-btn@2000:click",
                "#sidebar@1000:add-class=open",
                "#search@1500:type-text=example query",
                "#search-btn@1500:click",
                "#sidebar@1000:remove-class=open",
                "pause@2000"
              ]
            }'>
       </div>
       <script src="guidestar-controller.js"></script>
   </body>
   </html>
