"""
Sphinx extension entry point for guidestar.

Register the ``.. guidestar-demo::`` directive and ensure the
JavaScript / CSS assets are included in every built page.
"""

import os

from .directive import GuidestarDirective

_STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def setup(app):
    # Register the directive
    app.add_directive('guidestar-demo', GuidestarDirective)

    # Add the package's static directory so Sphinx copies it to _static/
    app.connect('builder-inited', _add_static_path)

    # Include JS and CSS on every page that might contain a guidestar
    app.add_js_file('guidestar-controller.js')
    app.add_css_file('guidestar-controls.css')

    return {
        'version': __import__('guidestar').__version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }


def _add_static_path(app):
    app.config.html_static_path.append(_STATIC_DIR)
