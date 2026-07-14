*** Settings ***
Documentation
...    Robot Framework capture script for the MAST JWST Observation Search demo.
...
...    Drives the real MAST search interface at build time, intercepts the
...    MAST search API with mock observation data via page.route(), and
...    captures four page states as a Guidestar screenshot wireframe.
...
...    The resulting wireframe + JSON config are written to
...    examples/wireframes/ and can be built into a self-contained demo
...    page with:  guidestar-build --configs-dir examples/wireframes --out _site
...
...    Prerequisites:
...        pip install "sphinx-guidestar[capture]"
...        playwright install chromium
...
...    Run:
...        guidestar-capture examples/rf/mast-jwst-search.robot \
...            --out examples/wireframes --rst --standalone
...
...    Note on selectors: The selectors below target the MAST Vue.js SPA.
...    If the MAST UI has changed since this file was written, inspect the
...    live page with browser DevTools and update the selectors accordingly.
...    The placeholder text and button text are the most stable identifiers.

Library    guidestar.rf.GuidestarCapture
...    capture_mode=screenshot
...    viewport=1440
...    height=720px

*** Variables ***
${MAST_JWST_URL}    https://mast.stsci.edu/search/ui/#/jwst
${MOCK_DATA_FILE}   ${CURDIR}/mast-jwst-mock.json

# Selectors — inspect the live page if any of these break after a MAST update.
# The MAST search UI is built with Vuetify; most interactive elements expose
# stable placeholder text or data-* attributes.
${SEL_TARGET_INPUT}     input[placeholder*="Target"], input[placeholder*="target"], #target-name-input
${SEL_SEARCH_BUTTON}    button[type="submit"], button:has-text("Search"), .search-btn
${SEL_RESULTS_TABLE}    .v-data-table__wrapper, .results-table, table.v-table

*** Test Cases ***
MAST JWST Observation Search Demo
    [Documentation]
    ...    Captures four steps of the JWST observation search workflow:
    ...    1. Initial search form (ready state)
    ...    2. Target name entered in the search input
    ...    3. Search results table loaded (from mock API)
    ...    4. Table scrolled to show more rows

    # ── Step 0 — Initial state ─────────────────────────────────────────────
    # Navigate to the MAST JWST search page.  The API mock must be registered
    # BEFORE the page makes its initial data requests (e.g. loading missions
    # list, column metadata), so Route API is called first.
    Open Capture    ${MAST_JWST_URL}    wait_until=networkidle

    # Mock the primary search endpoint.  The response envelope matches the
    # real MAST v0.1 search API — see mast-jwst-mock.json for the full
    # structure with 10 realistic NGC 1300 observations.
    Route API
    ...    **/api/v0.1/missions/search**
    ...    body_file=${MOCK_DATA_FILE}

    # Wait for the search form to be interactive
    Wait For Selector    ${SEL_TARGET_INPUT}    timeout=15000
    Wait For Timeout     800

    Capture Step
    ...    caption=^The JWST Observation Search form
    ...    delay=2500

    # ── Step 1 — Enter target name ─────────────────────────────────────────
    Fill Text    ${SEL_TARGET_INPUT}    NGC 1300

    Wait For Timeout     400
    Capture Step
    ...    caption=Enter a target name or sky coordinates
    ...    delay=2200

    # ── Step 2 — Search results ────────────────────────────────────────────
    Click Element    ${SEL_SEARCH_BUTTON}

    # The route mock returns instantly; wait for the Vue component to render
    Wait For Selector    ${SEL_RESULTS_TABLE}    timeout=12000
    Wait For Timeout     600

    Capture Step
    ...    caption=Observation results load from the mock API — no real network call
    ...    delay=3500

    # ── Step 3 — Scroll results ────────────────────────────────────────────
    # Scroll the results table to show the lower rows, demonstrating that the
    # demo captures the scrolled viewport state.
    Scroll Into View    ${SEL_RESULTS_TABLE}
    Evaluate    document.querySelector('${SEL_RESULTS_TABLE}').scrollTop = 180

    Wait For Timeout     500
    Capture Step
    ...    caption=Scroll through the observation list
    ...    delay=2500

    # ── Export ────────────────────────────────────────────────────────────
    Export Demo
    ...    mast-jwst-search
    ...    out_dir=${CURDIR}/../../examples/wireframes
    ...    rst=True
    ...    standalone=False
