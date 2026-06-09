guidestar
====================

A reusable infrastructure for embedding interactive wireframe demos
in Sphinx documentation and standalone HTML pages.

.. guidestar-demo:: _static/example-wireframe.html
   :steps: #demo-btn-1@1500:click|Click the first button, #demo-panel@1000:toggle-class=open|^Toggle the panel open, #demo-btn-2@1500:add-class=active|Activate the second button, #demo-input@1500:type-text=Hello World|Type into the input, #demo-btn-2@1500:remove-class=active, #demo-panel@1000:toggle-class=open|vClose the panel
   :height: 300px
   :repeat: true

Any package can provide its own HTML wireframe and a list of demo steps.
This package handles:

* Fetching and injecting the HTML into a container
* Overlaying play / pause / restart controls (Shadow DOM isolated)
* Stepping through actions (click, toggle-class, type-text, …) on a timer
* Pausing automatically when the user interacts with the demo
* Supporting multiple independent instances on the same page

.. toctree::
   :maxdepth: 1

   quickstart

.. toctree::
   :maxdepth: 1
   :caption: Creating Wireframes

   wireframe/manual
   wireframe/ai-assisted-vue
   wireframe/ai-assisted-url

.. toctree::
   :maxdepth: 1
   :caption: Demo Configuration

   demos/configuration
   demos/styling
   demos/accessibility

.. toctree::
   :maxdepth: 1
   :caption: Embedding

   embedding/sphinx
   embedding/html
   embedding/recording
   embedding/confluence

.. toctree::
   :maxdepth: 1
   :caption: GitHub Actions

   gh_actions/deploy-demos
   gh_actions/wireframe-review
