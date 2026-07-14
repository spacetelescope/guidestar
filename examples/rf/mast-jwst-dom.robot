*** Settings ***
Documentation    DOM-mode capture of MAST JWST Observation Search.

Library    guidestar.rf.GuidestarCapture
...    capture_mode=dom
...    viewport=1440
...    height=720px

*** Variables ***
${MAST_URL}      https://mast.stsci.edu/search/ui/#/jwst
${MOCK_FILE}     ${CURDIR}/mast-jwst-mock.json
${SEL_INPUT}     \#target-name-input
${SEL_SEARCH}    button.v-btn--block

*** Test Cases ***
MAST JWST Search Screenshot
    Route API    **/search/jwst/api/v0.1/search**    body_file=${MOCK_FILE}

    Open Capture    ${MAST_URL}    wait_until=networkidle
    Wait For Selector    ${SEL_INPUT}    timeout=20000
    Wait For Timeout    500

    Capture Step
    ...    caption=^The JWST Observation Search form
    ...    delay=2500

    Click Element    ${SEL_INPUT}
    Wait For Timeout    200
    Fill Text    ${SEL_INPUT}    NGC 1300
    Wait For Timeout    800
    Capture Step
    ...    caption=Enter an object name or sky coordinates
    ...    delay=2200

    Click Element    ${SEL_SEARCH}
    Wait For Timeout    4000
    Capture Step
    ...    caption=Search results load from the mock API
    ...    delay=3500

    Evaluate    window.scrollTo(0, 600)
    Wait For Timeout    600
    Capture Step
    ...    caption=Scroll through the observation list
    ...    delay=2500

    Export Demo
    ...    mast-jwst-dom
    ...    out_dir=${CURDIR}/../../examples/wireframes
    ...    standalone=True
