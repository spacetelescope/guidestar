"""Inspect all POST/GET requests after MAST JWST search."""
import sys, json
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 800})

    all_reqs = []
    def log_req(req):
        if req.method in ('POST', 'GET') and 'mast.stsci' in req.url:
            body = ''
            try:
                body = req.post_data or ''
                if body: body = body[:100]
            except Exception:
                pass
            all_reqs.append({'m': req.method, 'url': req.url[:100], 'body': body})
    page.on('request', log_req)

    all_resp = []
    def log_resp(resp):
        if resp.status == 200 and 'mast.stsci' in resp.url:
            try:
                data = resp.json()
                if isinstance(data, dict) and ('results' in data or 'data' in data):
                    r = data.get('results', data.get('data', []))
                    all_resp.append({
                        'url': resp.url[:100],
                        'keys': list(data.keys()),
                        'results_len': len(r),
                        'first': json.dumps(r[0])[:200] if r else None
                    })
            except Exception:
                pass
    page.on('response', log_resp)

    page.goto('https://mast.stsci.edu/search/ui/#/jwst',
              wait_until='networkidle', timeout=30000)

    inp = page.query_selector('#target-name-input')
    inp.click()
    page.wait_for_timeout(300)
    page.keyboard.type('NGC 1300')
    page.wait_for_timeout(800)

    for btn in page.query_selector_all('button'):
        if (btn.inner_text() or '').strip().upper() == 'SEARCH':
            btn.click()
            break

    page.wait_for_timeout(8000)

    # Log all API requests after load
    print('POST/API requests after search:')
    for r in all_reqs:
        if 'assets' not in r['url'] and 'fonts' not in r['url'].lower():
            print(f"  {r['m']} {r['url']}")
            if r['body']:
                print(f"    body: {r['body']}")

    print('\nJSON responses with results:')
    for r in all_resp:
        print(f"  {r['url']}: keys={r['keys']}, results={r['results_len']}")
        if r['first']:
            print(f"    first: {r['first']}")

    # screenshot scrolled
    page.evaluate('window.scrollTo(0, 1500)')
    page.wait_for_timeout(2000)
    page.screenshot(path='/tmp/mast3.png')
    browser.close()
    print('Done')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 800})

    all_responses = []
    def log_resp(resp):
        url = resp.url
        if 'jwst/api' in url and 'search' in url:
            try:
                data = resp.json()
                all_responses.append((url, data))
            except Exception:
                pass
    page.on('response', log_resp)

    print('Navigating...')
    page.goto('https://mast.stsci.edu/search/ui/#/jwst',
              wait_until='networkidle', timeout=30000)

    inp = page.query_selector('#target-name-input')
    inp.click()
    page.wait_for_timeout(300)
    page.keyboard.type('NGC 1300')
    page.wait_for_timeout(800)

    for btn in page.query_selector_all('button'):
        if (btn.inner_text() or '').strip().upper() == 'SEARCH':
            btn.click()
            print('Clicked SEARCH')
            break

    page.wait_for_timeout(10000)

    print(f'Total JWST API responses: {len(all_responses)}')
    for url, data in all_responses:
        results = data.get('results', [])
        info = data.get('info', [])
        total = data.get('totalResults', 0)
        print(f'  total={total} results={len(results)} info={len(info)}')
        if results:
            print(f'  First result keys: {list(results[0].keys())[:10]}')
            print(f'  First result sample: {json.dumps(results[0])[:300]}')

    # Check DOM
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(2000)
    for sel in ['tr', 'tbody tr', '.v-data-table', 'table',
                '[role="row"]', '.result-row', '[data-testid]']:
        els = page.query_selector_all(sel)
        if els:
            print(f'DOM {sel}: {len(els)} elements')

    page.screenshot(path='/tmp/mast_results2.png', full_page=False)
    browser.close()
    print('Done — screenshot at /tmp/mast_results2.png')
import sys, json
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 800})

    api_calls = []
    def log_request(request):
        url = request.url
        if '/api/' in url or 'search' in url.lower():
            api_calls.append((request.method, url[:120]))
    page.on('request', log_request)

    print('Navigating to MAST...')
    page.goto('https://mast.stsci.edu/search/ui/#/jwst',
              wait_until='networkidle', timeout=30000)

    # Inputs
    inputs = page.query_selector_all('input')
    print(f'\nInputs ({len(inputs)} total):')
    for inp in inputs[:8]:
        placeholder = inp.get_attribute('placeholder') or ''
        id_ = inp.get_attribute('id') or ''
        cls = (inp.get_attribute('class') or '')[:50]
        print(f'  id={id_!r:30} placeholder={placeholder!r:30} class={cls!r}')

    # Buttons
    btns = page.query_selector_all('button')
    print(f'\nButtons ({len(btns)} total, first 8):')
    for btn in btns[:8]:
        txt = (btn.inner_text() or '').strip()[:30]
        cls = (btn.get_attribute('class') or '')[:50]
        typ = btn.get_attribute('type') or ''
        print(f'  type={typ!r} text={txt!r:20} class={cls!r}')

    # API calls on load
    print(f'\nAPI calls on page load ({len(api_calls)}):')
    for method, url in api_calls[:10]:
        print(f'  {method} {url}')

    # Try filling and searching
    target_input = page.query_selector('#target-name-input')
    if target_input:
        # Capture real API response to understand the format
        responses = {}
        def log_response(response):
            url = response.url
            if 'jwst/api' in url and 'search' in url:
                try:
                    responses[url] = response.json()
                except Exception:
                    pass
        page.on('response', log_response)

        print(f'\nTarget input found: #target-name-input')
        target_input.click()
        page.wait_for_timeout(300)
        page.keyboard.type('NGC 1300')
        page.wait_for_timeout(500)

        # Find SEARCH button
        search_btn = None
        for btn in page.query_selector_all('button'):
            txt = (btn.inner_text() or '').strip().upper()
            if txt == 'SEARCH':
                search_btn = btn
                break
        if search_btn:
            print('Clicking SEARCH button...')
            search_btn.click()
            page.wait_for_timeout(8000)

            # Show response structure
            for url, data in responses.items():
                print(f'\nResponse from {url}:')
                if isinstance(data, dict):
                    print(f'  Keys: {list(data.keys())}')
                    for k, v in data.items():
                        if isinstance(v, list):
                            print(f'  {k}: list of {len(v)}')
                            if v:
                                print(f'  First item keys: {list(v[0].keys()) if isinstance(v[0], dict) else type(v[0])}')
                        else:
                            print(f'  {k}: {str(v)[:60]}')
                break

            # Find results elements
            print('\nAll visible non-empty text blocks:')
            for sel in ['td', 'tr', '.v-data-table', '.v-list-item', '[role="row"]',
                        '[role="gridcell"]', '.result', 'tbody']:
                els = page.query_selector_all(sel)
                if els:
                    print(f'  {sel}: {len(els)} elements')

            # Take screenshot
            page.screenshot(path='/tmp/mast_results.png', full_page=False)
            print('\nScreenshot saved to /tmp/mast_results.png')

    browser.close()
    print('\nDone.')
