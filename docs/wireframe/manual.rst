Manual
======

A wireframe is a **single, self-contained HTML file** that renders a static
or lightly-styled mockup of the target UI.  Guidestar fetches this file at
runtime, injects it into a sandboxed container, and drives the animation
steps against it.  Because the file is loaded via ``fetch`` and injected as
HTML, it must be fully self-contained — all CSS must live in a ``<style>``
block in ``<head>``; external stylesheets, scripts, images, and fonts should
not be referenced.


Structure
---------

A well-formed wireframe follows this pattern:

.. code-block:: text

   <html>
   └── <head>
       └── <style>          ← all CSS lives here (no external sheets)
   └── <body>
       └── root element     ← exactly one top-level wrapper div
           ├── interactive  ← buttons, inputs, selects …
           └── state        ← panels, badges, cards, toasts …

Key conventions:

* **Scripts: interaction-only, no external calls.**
  The wireframe should not fetch remote resources or manipulate the page
  outside its own root element.  However, a small ``<script>`` block is
  permitted — and encouraged — for click-to-toggle-class handlers that let
  users interact with the wireframe manually (e.g. opening a dropdown,
  dismissing a banner, toggling a checkbox state).  Use ``.onclick``
  property assignment rather than ``addEventListener`` so that guidestar
  can safely re-execute the script on demo restart without stacking
  duplicate listeners.  Do **not** embed any ``fetch()``,
  ``XMLHttpRequest``, ``WebSocket``, or ``setTimeout``/``setInterval``
  calls; all timed state changes are driven by guidestar steps.
* **IDs on every interactive element.** Steps address elements by CSS
  selector; each element that will be targeted by a step should have a
  unique ``id``.
* **Relative sizing.** Use ``%``, ``em``/``rem``, or ``flex``/``grid``
  layout so the wireframe scales cleanly inside the demo container without
  a fixed viewport.
* **Self-contained fonts.** Either use system font stacks or embed
  ``@font-face`` rules with base64-encoded font data.  Do not load Google
  Fonts or other external resources.
* **Neutral, accessible colours.** The wireframe will be viewed inside a
  documentation page that may use light or dark themes; aim for sufficient
  contrast at both ends.


Minimal example
---------------

The following wireframe renders a small app shell with a top bar, a
toggleable sidebar, and a content area.  It is the smallest structure that
exercises the most common step types.

.. code-block:: html

   <!DOCTYPE html>
   <html lang="en">
   <head>
   <meta charset="UTF-8">
   <style>
     *, *::before, *::after { box-sizing: border-box; }

     body { margin: 0; font-family: system-ui, sans-serif; }

     .app {
       background: #1e1e2e; color: #cdd6f4;
       min-height: 300px; display: flex; flex-direction: column;
       border-radius: 8px; overflow: hidden;
     }

     /* ── Top bar ── */
     .topbar {
       display: flex; align-items: center; gap: 8px;
       padding: 8px 12px; background: #181825;
       border-bottom: 1px solid #313244;
     }
     .topbar .logo { font-weight: 600; font-size: 14px; margin-right: auto; }
     .topbar button {
       background: #313244; color: #cdd6f4;
       border: 1px solid #45475a; border-radius: 6px;
       padding: 6px 14px; cursor: pointer; font-size: 13px;
     }
     .topbar button.active { border-color: #cba6f7; color: #cba6f7; }

     /* ── Sidebar ── */
     .sidebar {
       width: 0; overflow: hidden; background: #11111b;
       border-right: 1px solid #313244;
       transition: width 0.3s ease, padding 0.3s ease;
     }
     .sidebar.open { width: 200px; padding: 14px; }

     /* ── Content ── */
     .main { display: flex; flex: 1; }
     .content { flex: 1; padding: 16px; }
   </style>
   </head>
   <body>
   <div class="app">
     <div class="topbar">
       <span class="logo">MyApp</span>
       <button id="btn-settings">Settings</button>
       <button id="btn-run">Run</button>
     </div>
     <div class="main">
       <div class="sidebar" id="sidebar">
         <p>Sidebar content</p>
       </div>
       <div class="content" id="content">
         <p>Main content area</p>
       </div>
     </div>
   </div>
   </body>
   </html>

This wireframe can be animated with steps such as::

   :steps: #btn-settings@1000:click, #sidebar@800:toggle-class=open, #btn-run@1200:add-class=active


Kitchen-sink example
--------------------

The full kitchen-sink wireframe used throughout this documentation exercises
all common layout patterns — top bar, collapsible sidebar, cards, a log list,
a status bar, and a toast notification.  It is a useful starting point when
writing a new wireframe by hand.

Source:
`examples/wireframes/kitchen-sink.html <../../examples/wireframes/kitchen-sink.html>`_
