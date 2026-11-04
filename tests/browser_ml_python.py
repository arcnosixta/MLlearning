"""Verify the real browser Python runtime against a running Site build and its package CDN.

Run `python tests/browser_ml_python.py [http://127.0.0.1:8765]` with Playwright installed.
Use PLAYWRIGHT_CHANNEL=msedge to select the installed Edge browser on Windows.
"""

import csv
import json
import os
import re
import sys
from io import StringIO
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

from browser_ready import goto_ready


URL = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765').rstrip('/')
RUNTIME_TIMEOUT = 180_000
WAIT_FOREVER = 'while True:\n    pass\n'


def fetch(page, path):
    response = page.request.get(f'{URL}/{path}')
    assert response.ok, (response.status, response.url)
    return response


def open_editor(page, week, lang='ru'):
    goto_ready(page, f'{URL}/?lang={lang}#course/week/{week}')
    expect(page.locator('html')).to_have_attribute('lang', lang)
    page.locator('details.ml-code > summary').click()
    expect(page.locator('#ml-python-status')).to_have_attribute('data-state', 'ready')
    expect(page.locator('#ml-python-run')).to_be_enabled()


def run_code(page, source=None, expected_state='success'):
    if source is not None:
        page.locator('#ml-python-editor').fill(source)
    page.locator('#ml-python-run').click()
    status = page.locator('#ml-python-status')
    expect(status).to_have_attribute(
        'data-state', re.compile(r'^(success|error|stopped)$'), timeout=RUNTIME_TIMEOUT,
    )
    output = page.locator('#ml-python-output').text_content()
    assert status.get_attribute('data-state') == expected_state, (status.inner_text(), output)
    expect(page.locator('#ml-python-run')).to_be_enabled()
    expect(page.locator('#ml-python-stop')).to_be_disabled()
    return output


def start_loop(page):
    page.locator('#ml-python-editor').fill(WAIT_FOREVER)
    page.locator('#ml-python-run').click()
    expect(page.locator('#ml-python-status')).to_have_attribute(
        'data-state', 'running', timeout=RUNTIME_TIMEOUT,
    )
    expect(page.locator('#ml-python-stop')).to_be_enabled()
    assert len(page.workers) == 1
    return page.workers[0]


def assert_png(page):
    plot = page.locator('.ml-python-figures img')
    expect(plot).to_have_count(1)
    expect(plot).to_be_visible()
    plot.evaluate('img => img.decode()')
    assert plot.evaluate('img => img.naturalWidth > 0 && img.naturalHeight > 0')
    assert plot.evaluate('''async img => {
        const bytes = new Uint8Array(await (await fetch(img.src)).arrayBuffer());
        return [137, 80, 78, 71, 13, 10, 26, 10].every((byte, i) => byte === bytes[i]);
    }''')


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page = browser.new_page(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
    errors = []
    requests = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.context.on('request', lambda request: requests.append(request.url))

    open_editor(page, '01')
    original = fetch(page, 'ml/01/lab.py').text().replace('\r\n', '\n')
    assert page.locator('#ml-python-editor').input_value() == original
    assert not page.workers
    assert not any('pyodide' in urlsplit(request).path.lower() for request in requests)
    expected = fetch(page, 'ml/01/results.json').json()
    assert json.loads(run_code(page)) == expected
    experiment = page.locator('#ml-python-experiment')
    expect(experiment).to_be_visible()
    if experiment.get_attribute('open') is None:
        experiment.locator('summary').click()
    expect(experiment.locator('.ml-plot').first).to_be_visible()
    print('PASS lazy startup, real week 01 Python source and computed charts', flush=True)

    error = run_code(page, 'print("stdout marker")\nraise ValueError("traceback marker")\n', 'error')
    assert 'stdout marker' in error
    assert 'Traceback (most recent call last)' in error
    assert 'ValueError: traceback marker' in error
    page.locator('#ml-python-reset').click()
    expect(page.locator('#ml-python-editor')).to_have_value(original)
    assert 'математика 42' in run_code(page, 'print("математика", 6 * 7)\n')
    assert page.locator('#ml-python-output').evaluate('''output => {
        const style = getComputedStyle(output);
        return output.clientHeight >= 224 && parseFloat(style.fontSize) >= 16 &&
            style.whiteSpace === 'pre-wrap' && style.overflowWrap === 'anywhere' && style.resize === 'vertical';
    }''')

    assert 'plot marker' in run_code(page, '''\
import matplotlib.pyplot as plt
plt.plot([0, 1, 2], [0, 1, 4])
plt.title("Browser Python")
plt.show()
print("plot marker")
''')
    assert_png(page)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    print('PASS stdout, traceback, source reset and decoded matplotlib PNG on mobile', flush=True)

    worker = start_loop(page)
    with worker.expect_event('close', timeout=10_000):
        page.locator('#ml-python-stop').click()
    expect(page.locator('#ml-python-status')).to_have_attribute('data-state', 'stopped')
    assert 'after stop' in run_code(page, 'print("after stop")\n')

    worker = start_loop(page)
    with worker.expect_event('close', timeout=10_000):
        goto_ready(page, f'{URL}/?lang=ru#course')
    expect(page.locator('#ml-python-editor')).to_have_count(0)
    assert not page.workers
    print('PASS Stop, retry and worker cleanup on route change', flush=True)

    open_editor(page, '10', lang='kk')
    rows = list(csv.DictReader(StringIO(fetch(page, 'ml/10/data.csv').text())))
    visits = sum(int(row['visits']) for row in rows)
    assert f'dataset:{len(rows)}:{visits}:3' in run_code(page, '''\
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

data = pd.read_csv("data.csv")
labels = KMeans(n_clusters=3, random_state=17, n_init=10).fit_predict(data[["visits", "items"]])
sns.scatterplot(data=data, x="visits", y="items", hue=labels)
plt.show()
print(f"dataset:{len(data)}:{data['visits'].sum()}:{len(np.unique(labels))}")
''')
    assert_png(page)
    assert not errors, errors
    browser.close()

print('PASS bilingual editor, pandas, scikit-learn and Seaborn on the week 10 dataset', flush=True)
