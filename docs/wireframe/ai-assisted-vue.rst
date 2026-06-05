AI Assisted from Vue
====================

Wireframes that faithfully represent a real UI are time-consuming to write
from scratch.  An AI coding agent can dramatically speed up the process by
reading source code or rendering a live page and then producing a
self-contained HTML wireframe that matches the layout, styling, and key
interactive states of the original.

The prompt below is intended for use with a capable agentic coding
assistant (e.g. GitHub Copilot agent mode, Claude Code, or similar).  It
asks the agent to produce a file that satisfies the
:doc:`structural requirements <manual>` described in the Manual section —
in particular: a single ``<style>`` block, no ``<script>`` tags, IDs on
every interactive element, and no external resource references.

Use this prompt when the target application lives in a local or remote
repository built with Vue (or a similar component-based framework).  Adjust
the repository path and the list of components to focus on as needed.

.. code-block:: text

   You are helping me build a guidestar wireframe — a self-contained HTML
   mockup used to animate a UI demo in documentation.

   Please prompt for the location of the repository, explore the files, and
   produce a single file called wireframe.html that represents the main
   application shell.

   Requirements for the wireframe:
   - One self-contained HTML file: all CSS in a <style> block in <head>,
     no external stylesheets, no <script> tags, no external fonts or images.
   - Reproduce the overall layout: top bar / toolbar, sidebar or panel
     structure, main content area, status bar — whatever the app uses.
   - Reproduce the visual style: colours, typography scale, border radii,
     spacing, and iconography (use unicode characters or simple SVG inline
     for icons rather than icon font classes).
   - Give every interactive element (buttons, inputs, selects, tabs,
     toggleable panels) a unique id attribute so that guidestar step
     selectors can target them.
   - Include representative placeholder content (realistic labels, a few
     list items, example data) that reflects what a real user would see.
   - Do NOT include any JavaScript.  State changes (open/close panels,
     active states, etc.) will be driven by guidestar's CSS-class-toggle
     actions, so model both the default state and the toggled state purely
     in CSS using class variants (e.g. .panel, .panel.open).

   Suggested approach:
   1. Read the top-level Vue components (App.vue, Layout.vue, or equivalent)
      to understand the overall shell structure.
   2. Read the component files for the toolbar, sidebar, and main content
      area to extract colours (check tailwind.config.js, tokens, or CSS
      custom properties), spacing, and element structure.
   3. Read any existing Storybook stories or test fixtures for realistic
      sample data.
   4. Produce wireframe.html.

   Focus on the layout skeleton and interactive affordances rather than
   pixel-perfect fidelity.  The wireframe does not need to be functional —
   it only needs to look convincing when static CSS classes are toggled.
