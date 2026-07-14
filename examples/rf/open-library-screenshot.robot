*** Settings ***
Documentation
...    Captures the Open Library search demo in both screenshot and DOM modes.
...    Used to produce the side-by-side comparison embedded in the
...    Robot Framework Capture documentation page (docs/wireframe/rf-capture.rst).
...
...    Run:
...        conda run -n wireframe-demo guidestar-capture \
...            examples/rf/open-library-screenshot.robot \
...            --out examples/wireframes --standalone
...
...        conda run -n wireframe-demo guidestar-capture \
...            examples/rf/open-library-dom.robot \
...            --out examples/wireframes --standalone

Library    guidestar.rf.GuidestarCapture
...    capture_mode=screenshot
...    viewport=960
...    height=460px

*** Variables ***
${APP_URL}     file://${CURDIR}/live-app.html
${MOCK_FILE}   ${CURDIR}/packages-mock.json
${SEL_BTN}     \#pkg-btn
${SEL_INPUT}   \#pkg-input
${SEL_RESULT}  .result-card

*** Test Cases ***
Package Registry Search Screenshot Demo
    Route API    **/api/packages**    body_file=${MOCK_FILE}

    Open Capture    ${APP_URL}    wait_until=load
    Wait For Selector    ${SEL_BTN}    timeout=5000

    Capture Step
    ...    caption=^Package Registry Search
    ...    delay=2000

    Fill Text    ${SEL_INPUT}    astronomy
    Wait For Timeout    300
    Capture Step
    ...    caption=Type a search query
    ...    delay=2000

    Click Element    ${SEL_BTN}
    Wait For Selector    ${SEL_RESULT}    timeout=6000
    Wait For Timeout    200
    Capture Step
    ...    caption=Results appear from the demo\u2019s mock data \u2014 no real API request was made
    ...    delay=3500

    Export Demo
    ...    open-library-screenshot
    ...    out_dir=${CURDIR}/../wireframes
    ...    standalone=True
