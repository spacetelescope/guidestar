"""
guidestar.rf — Robot Framework keyword library for capturing live-page demos.

The GuidestarCapture library drives a real browser (via Playwright) against
any URL, intercepts API calls with mock data, and captures the page state at
each marked step.  The result is a static wireframe HTML file that can be
used by guidestar-build and embedded in documentation — with no live page
injection required at view time.

Usage in a .robot file::

    *** Settings ***
    Library    guidestar.rf.GuidestarCapture    capture_mode=screenshot

    *** Test Cases ***
    My Demo
        Open Capture    https://example.com
        Route API       **/api/search**    body={"results": []}
        Wait For Selector    #search-input
        Capture Step    caption=The search form
        Fill Text       #search-input    hello world
        Click Element   #search-btn
        Wait For Selector    .results
        Capture Step    caption=Search results
        Export Demo     my-demo    out_dir=examples/wireframes
"""
from .capture_library import GuidestarCapture

__all__ = ["GuidestarCapture"]
