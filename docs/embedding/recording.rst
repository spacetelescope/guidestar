Recording as GIF
================

Guidestar demos can be recorded as animated GIFs for use in contexts that
don't support JavaScript — such as Confluence, README files, or slide decks.
The recording is performed by a headless browser that plays back the demo
and captures frames, then assembles them into a looping GIF.


From a Wireframe
----------------

The ``examples/record.py`` script opens each built demo page in headless
Chromium, captures frames during one full playback cycle, and assembles them
into an animated GIF.  Playback controls are hidden during recording.


How it works
^^^^^^^^^^^^

1. **Wireframes** are authored once in ``examples/wireframes/`` — these are
   the layout and styling for your demo UI.

2. **Demo configs** live in ``examples/demos/`` as JSON files.  Each config
   references a wireframe and defines the step sequence:

   .. code-block:: json

      {
        "wireframe": "kitchen-sink.html",
        "title": "Kitchen Sink — All Built-in Actions",
        "steps": [
          "#btn-sidebar@1800:click",
          "#sidebar@800:toggle-class=open",
          "#input-search@1500:set-value=pipeline"
        ],
        "repeat": true,
        "height": "420px"
      }

   Multiple configs can reference the **same wireframe** with different
   step sequences.

3. **A build script** (``examples/build.py``) combines each config with its
   wireframe and inlines the controller JS and CSS into a single
   self-contained HTML page.

4. **The recording script** (``examples/record.py``) plays each page and
   produces a GIF.


Running locally
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Build self-contained HTML pages
   python examples/build.py

   # Record animated GIFs (requires: pip install playwright Pillow
   # and: playwright install chromium)
   python examples/record.py

   # Check the output
   ls _site/*.html _site/*.gif


Recording options
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python examples/record.py --fps 10 --width 800         # defaults
   python examples/record.py --demo kitchen-sink-full      # one demo only
   python examples/record.py --site _site --out _site      # custom dirs

Higher ``--fps`` produces smoother GIFs but larger files.  The default of
10 fps is a good balance.


Demo config reference
^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 20 15 65
   :header-rows: 1

   * - Key
     - Default
     - Description
   * - ``wireframe``
     - (required)
     - Filename of the wireframe HTML in ``examples/wireframes/``
   * - ``title``
     - ``"Wireframe Demo"``
     - Page ``<title>``
   * - ``steps``
     - ``[]``
     - Array of step shorthand strings or step objects
   * - ``repeat``
     - ``true``
     - Loop the demo on completion
   * - ``autoStart``
     - ``true``
     - Start automatically when visible
   * - ``height``
     - ``"100vh"``
     - Container height in the built page
   * - ``pauseOnInteraction``
     - ``true``
     - Pause on user clicks inside the demo
   * - ``initialClass``
     - ``""``
     - CSS class(es) applied to the content root on load

See :doc:`../demos/configuration` for full details on step syntax and options.


Reusing wireframes with different step sequences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The same wireframe can power multiple demos.  For example:

.. code-block:: text

   examples/
     wireframes/
       kitchen-sink.html          ← one wireframe
     demos/
       kitchen-sink-full.json     ← long demo (all actions)
       kitchen-sink-short.json    ← short demo (highlights only)

Both JSON configs reference ``"wireframe": "kitchen-sink.html"`` but define
different step sequences.  The build script produces a separate
self-contained HTML page and GIF for each.


From a Live URL
---------------

.. note::

   Recording from a live URL is **coming soon**.  This feature will allow
   you to point the recorder at any running web application and capture a
   GIF of the real UI without authoring a wireframe.
