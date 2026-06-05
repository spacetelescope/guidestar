Demo Options
============

Config object
-------------

When creating a ``Guidestar`` programmatically or via the
``data-guidestar-config`` attribute, the following properties are supported:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Property
     - Type
     - Default
     - Description
   * - ``htmlSrc``
     - string
     - ``null``
     - URL of the HTML file to fetch and inject into the container.
   * - ``steps``
     - array
     - ``[]``
     - Array of step objects or shorthand strings (see below).
       When empty, the demo renders in **static mode** — no playback
       controls, timeline, or autostart (see :ref:`static-render`).
   * - ``initSteps``
     - array
     - ``[]``
     - Steps executed synchronously before playback begins (or before the
       static render is shown). Init steps run with no delay, no highlight
       animation, and no cursor movement — they are intended to set up the
       initial DOM state. Each object supports the non-time-based fields
       from the step format: ``target``, ``action`` / ``actions``, ``value``,
       ``noHighlight``, ``caption``, and ``captionOptions``. The ``delay``
       field is accepted but ignored. In static mode the cursor (if enabled)
       is placed at the last init step's target element, and the last caption
       persists as a static overlay.
   * - ``repeat``
     - bool
     - ``true``
     - Whether to loop the demo when it reaches the end.
   * - ``autoStart``
     - bool
     - ``true``
     - Start automatically when the container is visible in the viewport.
   * - ``pauseOnInteraction``
     - bool
     - ``true``
     - Pause the demo when the user clicks inside the container.
   * - ``cursor``
     - bool
     - ``true``
     - Show an animated cursor that moves to each target element before the
       action executes. Set to ``false`` to disable.
   * - ``cursorSpeed``
     - number
     - ``300``
     - Duration in milliseconds for the cursor movement animation.
   * - ``timeline``
     - bool
     - ``true``
     - Show an interactive progress timeline at the bottom of the container
       on hover. Each step is represented as a dot; filled dots indicate
       completed steps. Click a dot to jump to that step. Set to ``false``
       to disable (also skips HTML snapshot caching used for backward
       navigation).
   * - ``reduceMotion``
     - bool / string
     - ``'auto'``
     - Controls reduced-motion behaviour. ``'auto'`` (default) honours the
       operating system's ``prefers-reduced-motion`` setting. ``true`` forces
       all animations off regardless of OS preference. ``false`` keeps
       animations on even when the OS requests reduced motion. See
       :doc:`accessibility` for details.
   * - ``autoScroll``
     - bool
     - ``true``
     - When ``true`` (the default), guidestar automatically scrolls a step's
       target element into view before executing the action, if the element
       is not already fully visible in its scrollable ancestor.  The scroll
       is smooth and accompanied by a brief ↓ indicator badge.  Set to
       ``false`` to disable all automatic scrolling.  Individual steps can
       also opt out by appending ``~`` to the delay (e.g.
       ``#el@800~:click``).
   * - ``viewport``
     - number / null
     - ``null``
     - Fixed viewport width (in CSS pixels) at which the wireframe was
       designed.  When set, the wireframe content is rendered internally at
       that width and then scaled uniformly (``transform: scale()``) to fit
       the demo container, preserving the exact layout of the original
       design.  When ``null`` (the default), the wireframe reflows
       responsively to match the container width.

       Use **scale mode** (set a number) for wireframes captured from a
       live URL at a specific desktop viewport — this guarantees the
       content always looks exactly like the captured screenshot.
       Use **responsive mode** (``null``) for wireframes hand-authored
       to adapt to their container, such as the kitchen-sink example.
   * - ``fullscreen``
     - bool
     - ``true``
     - Show a fullscreen toggle button in the top-right corner of the
       container.  The button is hidden by default and becomes visible on
       hover or when the demo is paused.  Clicking it calls the browser's
       Fullscreen API on the container element; pressing :kbd:`Escape`
       exits.  Set to ``false`` to hide the button.

       In the Sphinx directive, use ``:fullscreen: false``.
   * - ``resizable``
     - bool
     - ``true``
     - Show a drag handle in the bottom-right corner of the container.
       Dragging it resizes the container's width and height; a live
       ``W × H`` badge is shown while dragging.  The handle is hidden by
       default and fades in on hover.  Set to ``false`` to disable.

       In the Sphinx directive, use ``:resizable: false``.
   * - ``poweredby``
     - bool
     - ``true``
     - Show a small "demo powered by guidestar" badge in the bottom-left
       corner of the container (to the left of the timeline).  The badge
       displays the guidestar logo icon, links to
       `guidestar.readthedocs.io <https://guidestar.readthedocs.io>`_,
       and shows a "demo powered by guidestar" tooltip on hover.  Like the
       timeline, it is hidden by default and fades in when the container
       is hovered.  Set to ``false`` to hide the badge entirely.

       In the Sphinx directive, use ``:poweredby: false``.
   * - ``onStepStart``
     - function
     - ``null``
     - Callback ``(stepIndex, step)`` called before each step executes.
   * - ``onStepEnd``
     - function
     - ``null``
     - Callback ``(stepIndex, step)`` called after each step executes.
   * - ``onComplete``
     - function
     - ``null``
     - Callback called when the sequence finishes (before repeat loop).


Step format
-----------

Steps can be provided as **JSON objects** or **shorthand strings**.


.. _json-object-format:

JSON object format
^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "target": "#my-element",
     "action": "click",
     "delay": 1500,
     "value": null,
     "noHighlight": false,
     "caption": "Click the element",
     "captionOptions": { "position": "bottom" }
   }

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Field
     - Required
     - Description
   * - ``target``
     - no
     - CSS selector for the target element (inside the injected HTML).
       Omit for ``pause`` actions.
   * - ``action``
     - yes
     - Action name (see table below).
   * - ``delay``
     - no
     - Milliseconds to hold on this step before advancing (default ``2000``).
   * - ``value``
     - no
     - Action-specific value (e.g. class name for ``toggle-class``).
   * - ``noHighlight``
     - no
     - If ``true``, skip the highlight animation on this step.
   * - ``caption``
     - no
     - Text to display as a semi-transparent caption overlay during this step.
   * - ``captionOptions``
     - no
     - Object with optional keys: ``position`` (``"top"``, ``"bottom"``, or
       ``"auto"``; default ``"auto"``) and ``className`` (extra CSS class to
       apply to the caption element for this step).


Multi-action steps
^^^^^^^^^^^^^^^^^^

A step can execute **multiple actions at once** by providing an ``actions``
array instead of a single ``action`` field. By default sub-actions run
synchronously (no delay between them), and the step's ``delay`` applies
after all actions have executed.

This is useful when several DOM changes should appear simultaneously —
for example, updating an image and its legend in the same visual beat,
or toggling a class while also setting text.

.. code-block:: json

   {
     "actions": [
       { "target": "#sidebar", "action": "toggle-class", "value": "open" },
       { "target": "#status", "action": "set-text", "value": "Ready" }
     ],
     "delay": 1500,
     "caption": "Open sidebar and update status"
   }

Individual sub-actions can include an optional ``delay`` (in ms) to pause
before the next sub-action executes. This is useful for showing cause and
effect within a single step — for example, clicking a button and then
revealing the result after a short pause:

.. code-block:: json

   {
     "actions": [
       { "action": "click-button", "value": "Load", "delay": 500 },
       { "action": "viewer-add", "value": "horiz:Image" },
       { "action": "viewer-image", "value": "Image:photo.png" }
     ],
     "delay": 3000,
     "caption": "Load the data"
   }

Sub-action delays do not create individual timeline dots, captions, or
steppable positions — they are purely visual timing within one step.
The delay on the last sub-action is also respected before the step's
top-level ``delay`` begins.

Each object in the ``actions`` array supports:

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Field
     - Required
     - Description
   * - ``target``
     - no
     - CSS selector for the sub-action's target element.
   * - ``action``
     - yes
     - Action name (same set as single-action steps).
   * - ``value``
     - no
     - Action-specific value.
   * - ``delay``
     - no
     - Milliseconds to wait after this sub-action before executing the next
       one. Defaults to ``0`` (immediate). Respects the current playback
       speed.

The top-level ``delay``, ``caption``, ``captionOptions``, and
``noHighlight`` fields work the same as on a single-action step. The
cursor (if enabled) moves to the first sub-action's target element.


Shorthand string format
^^^^^^^^^^^^^^^^^^^^^^^

::

   target@delay:action=value|caption text

Examples:

.. code-block:: text

   #btn@1500:click                    → click #btn, hold 1500ms
   #panel@1000:toggle-class=open      → toggle “open” class, hold 1000ms
   #btn@1500!:click                   → click (no highlight), hold 1500ms   #btn@1500~:click                   → click, skip auto-scroll for this step   pause@3000                         → wait 3 seconds
   #el:highlight                      → highlight with default 2000ms delay
   #input@1000:set-value=Hello        → set input value to “Hello”   #input@1500:type-text=Hello World   → type "Hello World" letter-by-letter   #btn@1500:click|Click me           → click with auto-positioned caption
   #btn@1500:click|^Click me          → click with caption forced to top
   #btn@1500:click|vClick me          → click with caption forced to bottom

Caption text follows the ``|`` pipe character at the end of the string.
Prefix the caption with ``^`` to force it to the **top** of the container,
or ``v`` to force it to the **bottom**. Without a prefix, the position is
chosen automatically (opposite the target element’s vertical position).


Supported actions
-----------------

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Action
     - Value
     - Description
   * - ``click``
     - —
     - Simulate a click on the target element.
   * - ``add-class``
     - class name(s)
     - Add one or more CSS classes (space-separated).
   * - ``remove-class``
     - class name(s)
     - Remove one or more CSS classes.
   * - ``toggle-class``
     - class name(s)
     - Toggle one or more CSS classes.
   * - ``set-attribute``
     - ``name:value``
     - Set an HTML attribute. Use colon to separate name and value.
   * - ``remove-attribute``
     - attr name
     - Remove an HTML attribute.
   * - ``set-value``
     - value
     - Set ``.value`` on an input/select and dispatch ``input``/``change`` events.
   * - ``type-text``
     - text
     - Animate typing text into an input or element over the step's delay.
       Automatically uses letter-at-a-time for short text or word-at-a-time
       for long text, based on what yields a comfortable typing speed.
   * - ``set-text``
     - text
     - Set ``.textContent`` of the target.
   * - ``set-html``
     - html
     - Set ``.innerHTML`` of the target. Use with caution.
   * - ``scroll-into-view``
     - —
     - Smoothly scroll the target into view using the browser's native
       ``scrollIntoView`` API.  Use ``scroll-to`` instead when you want
       guidestar's auto-scroll behaviour (centres the element, shows the
       \u2193 indicator badge).
   * - ``scroll-to``
     - —
     - Scroll the target element into view within its nearest scrollable
       ancestor, centring it vertically.  Shows the animated \u2193 scroll
       indicator badge.  This is the explicit form of the auto-scroll that
       normally happens automatically before every action when
       ``autoScroll: true``.
   * - ``dispatch-event``
     - ``eventName`` or ``eventName:detailJSON``
     - Dispatch a ``CustomEvent`` on the target.
   * - ``highlight``
     - —
     - Temporarily highlight the target (default action when no action is specified).
   * - ``pause``
     - —
     - Wait for the step's delay without performing any action.


Custom actions
--------------

Packages can register their own domain-specific actions:

.. code-block:: javascript

   Guidestar.registerAction('select-tab', function(step, el, contentRoot) {
       // "this" is the Guidestar instance
       var tabs = contentRoot.querySelectorAll('.tab');
       tabs.forEach(function(tab) {
           tab.classList.remove('active');
           if (tab.textContent.trim() === step.value) {
               tab.classList.add('active');
           }
       });
   });

The handler receives:

- ``step`` — the full step object
- ``el`` — the resolved target element (may be ``null``)
- ``contentRoot`` — the container element holding the injected HTML
- ``this`` — the ``Guidestar`` instance (access ``this.pause()``, ``this.play()``, etc.)


Captions (transcript overlay)
------------------------------

Each step can optionally display a **caption** — a semi-transparent text
overlay that appears at the top or bottom of the demo container, similar to
closed captions on a video. Captions are useful for narrating a demo
walkthrough.


Adding captions
^^^^^^^^^^^^^^^

**Shorthand syntax** — append ``|text`` to any step string:

.. code-block:: text

   #btn-sidebar@1800:click|Open the sidebar
   pause@2000|Wait for the animation to finish

To force the caption position, prefix the text with ``^`` (top) or ``v``
(bottom):

.. code-block:: text

   #btn-sidebar@1800:click|^This caption appears at the top
   #status-bar@1000:highlight|vThis caption appears at the bottom

**JSON object syntax** — use the ``caption`` and ``captionOptions`` fields:

.. code-block:: json

   {
     "target": "#input-search",
     "action": "type-text",
     "value": "pipeline",
     "delay": 1500,
     "caption": "Search for a pipeline",
     "captionOptions": {
       "position": "top",
       "className": "my-custom-caption"
     }
   }

``captionOptions`` fields:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Description
   * - ``position``
     - ``"top"``, ``"bottom"``, or ``"auto"`` (default). When ``"auto"``,
       the caption is placed opposite the target element — if the target
       is in the top half of the container the caption appears at the
       bottom, and vice versa. Steps without a target (e.g. ``pause``)
       default to the bottom.
   * - ``className``
     - An extra CSS class applied to the caption element for this step,
       allowing per-step styling.

Steps without a ``caption`` (or with an empty string) will hide any
previously visible caption.


Styling captions
^^^^^^^^^^^^^^^^

Caption appearance is controlled via CSS custom properties set on the
``[data-guidestar]`` container:

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Property
     - What it controls
     - Default
   * - ``--gs-caption-bg``
     - Background color
     - ``rgba(0,0,0,0.72)``
   * - ``--gs-caption-color``
     - Text color
     - ``#fff``
   * - ``--gs-caption-font-size``
     - Font size
     - ``14px``
   * - ``--gs-caption-padding``
     - Padding
     - ``10px 16px``
   * - ``--gs-caption-inset``
     - Left & right inset — centres the caption and keeps it clear of the
       control button
     - ``68px``

The following additional custom properties control the new fullscreen button
and can be set on the ``[data-guidestar]`` container:

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Property
     - What it controls
     - Default
   * - ``--gs-control-top``
     - Top offset of the fullscreen button
     - ``12px``

Example:

.. code-block:: css

   [data-guidestar] {
       --gs-caption-bg: rgba(0, 0, 80, 0.85);
       --gs-caption-font-size: 16px;
       --gs-caption-padding: 12px 20px;
   }


.. _static-render:

Static render mode
------------------

When no ``steps`` are provided, the demo operates in **static render mode**.
The playback controls, timeline, and restart overlay are not created, and
autostart is skipped.  The wireframe is simply shown at whatever state
``initSteps`` leaves it in.

This is useful when you want to show a screenshot-like view of the wireframe
at a specific state — for example, with a sidebar open, a field filled in,
or a cursor resting over a particular element.


Setting the visual state
^^^^^^^^^^^^^^^^^^^^^^^^

Use ``initSteps`` to drive the wireframe into the desired state.  All normal
actions (``add-class``, ``set-value``, ``click``, etc.) are supported;  time-
based fields (``delay``) are ignored.

.. code-block:: json

   {
     "initSteps": [
       { "target": "#sidebar", "action": "add-class", "value": "open" },
       { "target": "#search-input", "action": "set-value", "value": "jwst" }
     ]
   }


Cursor placement
^^^^^^^^^^^^^^^^

When ``cursor`` is ``true`` (the default), the cursor is placed at the centre
of the last init step that has a ``target``.  Set ``cursor`` to ``false`` to
hide the cursor entirely.

.. code-block:: json

   {
     "initSteps": [
       { "target": "#sidebar", "action": "add-class", "value": "open" },
       { "target": "#search-input", "action": "set-value", "value": "jwst",
         "caption": "Search pre-filled with a query" }
     ]
   }

The cursor rests on ``#search-input`` because it is the last targeted step.


Persistent caption
^^^^^^^^^^^^^^^^^^

A ``caption`` on the last init step persists as a static overlay.  Use
``captionOptions`` to control position as normal.


Directive example
^^^^^^^^^^^^^^^^^

.. code-block:: rst

   .. guidestar-demo:: _static/app.html
      :init-steps-json:
         [
           {"target": "#sidebar", "action": "add-class", "value": "open"},
           {"target": "#run-btn",
            "caption": "Ready to run",
            "captionOptions": {"position": "bottom"}}
         ]
      :height: 420px

This renders a static wireframe with the sidebar open, the cursor resting on
``#run-btn``, and a caption at the bottom.

To hide the cursor:

.. code-block:: rst

   .. guidestar-demo:: _static/app.html
      :init-steps-json: [{"target": "#sidebar", "action": "add-class", "value": "open"}]
      :cursor: false
      :height: 420px
