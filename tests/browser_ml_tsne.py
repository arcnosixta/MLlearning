"""Exercise practice 10 t-SNE in real Pyodide, including edits and RU/KK UI.

Run after scripts/build.py; starts its own local server unless a URL is passed.
PLAYWRIGHT_CHANNEL=msedge uses installed Edge on Windows.
"""
import functools
import http.server
import json
import math
import os
import subprocess
import sys
import threading
import time

from playwright.sync_api import expect, sync_playwright

from browser_ml_examples import (
    ROOT, QuietHandler, assert_figures, open_editor, run_ui, run_worker, source,
)
from browser_ready import goto_ready

ARTIFACTS = ROOT / 'artifacts/tsne-qa'
ARTIFACTS.mkdir(parents=True, exist_ok=True)
MARKER = '__TSNE_QA__'


def observed_source(code):
    """Record real estimator inputs/results without product-only debug hooks."""
    return '''
import json
import time
import pandas
import matplotlib.pyplot
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

_qa_tsne = TSNE.fit_transform
_qa_kmeans = KMeans.fit
_qa_records = {"tsne": [], "kmeans": []}

def _qa_observe_tsne(self, matrix, *args, **kwargs):
    started = time.perf_counter()
    projection = _qa_tsne(self, matrix, *args, **kwargs)
    _qa_records["tsne"].append({
        "seconds": time.perf_counter() - started,
        "params": self.get_params(),
        "input": matrix.tolist(),
        "points": projection.tolist(),
    })
    return projection

def _qa_observe_kmeans(self, matrix, *args, **kwargs):
    result = _qa_kmeans(self, matrix, *args, **kwargs)
    _qa_records["kmeans"].append({
        "clusters": self.n_clusters,
        "input": matrix.tolist(),
        "labels": self.labels_.tolist(),
    })
    return result

TSNE.fit_transform = _qa_observe_tsne
KMeans.fit = _qa_observe_kmeans
try:
    exec(compile(''' + repr(code) + ''', "lab.py", "exec"), globals())
finally:
    TSNE.fit_transform = _qa_tsne
    KMeans.fit = _qa_kmeans
print("''' + MARKER + '''" + json.dumps(_qa_records, allow_nan=False))
'''


def diagnostic(stdout):
    public, marker, raw = stdout.rpartition(MARKER)
    assert marker, stdout
    return public, json.loads(raw)


def max_delta(left, right):
    assert len(left) == len(right)
    return max(abs(a - b) for row_a, row_b in zip(left, right)
               for a, b in zip(row_a, row_b))


def check_projection(record, perplexity):
    matrix, points = record['input'], record['points']
    assert len(matrix) == len(points) == 72
    assert all(len(row) == 4 for row in matrix)
    assert all(len(point) == 2 and all(map(math.isfinite, point)) for point in points)
    for index in range(4):
        column = [row[index] for row in matrix]
        assert abs(sum(column) / 72) < 1e-10
        assert abs(sum(value ** 2 for value in column) / 72 - 1) < 1e-10
    assert record['params']['perplexity'] == perplexity
    assert record['params']['random_state'] is not None
    assert record['params']['max_iter'] >= 250


def native_observation(code):
    env = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', IMLEARNING_LANG='ru')
    native_code = 'import matplotlib.pyplot as _native_pyplot\n_native_pyplot.show = lambda *args, **kwargs: None\n' + observed_source(code)
    completed = subprocess.run([sys.executable, '-c', native_code],
        cwd=ROOT / 'dist/ml/10', env=env, encoding='utf-8',
        capture_output=True, timeout=90, check=True)
    assert not completed.stderr, completed.stderr
    return diagnostic(completed.stdout)


def edited_perplexity(code, value):
    before = 'PERPLEXITY = 15'
    assert before in code
    return code.replace(before, f'PERPLEXITY = {value}', 1)


def equal_units(svg, case):
    """One coordinate unit must occupy the same SVG distance on both axes."""
    points = [point for series in case['series'] for point in series['points']]
    marks = svg.locator('circle').evaluate_all(
        'circles => circles.map(c => [Number(c.getAttribute("cx")), Number(c.getAttribute("cy"))])')
    assert len(points) == len(marks) == 72
    for index in range(1, 72):
        dx, dy = points[index][0] - points[0][0], points[index][1] - points[0][1]
        if abs(dx) > 0.1 and abs(dy) > 0.1:
            scale_x = abs((marks[index][0] - marks[0][0]) / dx)
            scale_y = abs((marks[index][1] - marks[0][1]) / dy)
            assert math.isclose(scale_x, scale_y, rel_tol=1e-9), (scale_x, scale_y)
            return
    raise AssertionError('Need a nondegenerate point pair to test chart geometry')


def main():
    server = None
    if len(sys.argv) > 1:
        url = sys.argv[1].rstrip('/')
    else:
        handler = functools.partial(QuietHandler, directory=str(ROOT / 'dist'))
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}'
    report = {'worker': [], 'ui': [], 'nativeComparison': {}}
    code = source('10')
    expected = json.loads(source('10', 'results.json'))
    assert len(expected['topics']) == 5
    native_public, native = native_observation(code)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
        page = browser.new_page(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        goto_ready(page, f'{url}/?lang=ru#course')
        page.evaluate("window.qaId = 0; window.qaWorker = new Worker('ml/python-worker.js', {type:'module'});")
        originals = {}
        for language in ('ru', 'kk'):
            for perplexity in (15, 5, 30):
                started = time.monotonic()
                stdout, stderr, result = run_worker(page,
                    observed_source(edited_perplexity(code, perplexity)), language, '10')
                public, records = diagnostic(stdout)
                assert public.strip() and len(public) < 5000 and '"topics"' not in public
                assert not stderr, stderr
                assert len(result['figures']) == 2
                assert_figures(page, result['figures'])
                assert len(records['tsne']) == 1
                check_projection(records['tsne'][0], perplexity)
                model = [item for item in records['kmeans'] if item['clusters'] == 3][-1]
                assert max_delta(model['input'], records['tsne'][0]['input']) == 0
                if perplexity == 15:
                    originals[language] = (public, records, result)
                    if language == 'ru':
                        report['nativeComparison']['inputMaxDelta'] = max_delta(
                            native['tsne'][0]['input'], records['tsne'][0]['input'])
                        report['nativeComparison']['shortPointsMaxDelta'] = max_delta(
                            native['tsne'][0]['points'], records['tsne'][0]['points'])
                else:
                    assert records['tsne'][0]['points'] != originals[language][1]['tsne'][0]['points']
                report['worker'].append({'language': language, 'perplexity': perplexity,
                    'fitSeconds': records['tsne'][0]['seconds'], 'totalSeconds': round(time.monotonic() - started, 3),
                    'stdoutChars': len(public), 'figures': len(result['figures'])})
                print(f'PASS {language} perplexity={perplexity}: 72 standardized rows, two PNGs; fit {records["tsne"][0]["seconds"]:.3f}s', flush=True)
            for invalid in (0, -1, 72):
                stdout, stderr, failure = run_worker(page,
                    edited_perplexity(code, invalid), language, '10', expected='error')
                assert 'ValueError' in failure['message'] and 'PERPLEXITY' in failure['message']
                localized = ('должна быть больше 0 и меньше 72' if language == 'ru'
                             else '0-ден үлкен, 72 мәнінен кіші болуы керек')
                assert localized in failure['message'], failure['message']
                assert '"topics"' not in stdout
                report['worker'].append({'language': language, 'invalidPerplexity': invalid,
                    'error': failure['message'].splitlines()[-1]})
        assert originals['ru'][0] != originals['kk'][0]
        stdout, stderr, result = run_worker(page, observed_source(code), 'ru', '10')
        public, repeated = diagnostic(stdout)
        assert not stderr
        assert repeated['tsne'][0]['points'] == originals['ru'][1]['tsne'][0]['points']
        assert result['figures'] == originals['ru'][2]['figures']
        print('PASS invalid parameters, error recovery and deterministic repeated t-SNE', flush=True)

        assert 'CLUSTERS = 3' in code
        stdout, stderr, result = run_worker(page,
            observed_source(code.replace('CLUSTERS = 3', 'CLUSTERS = 2', 1)), 'ru', '10')
        public, records = diagnostic(stdout)
        model = [item for item in records['kmeans'] if item['clusters'] == 2][-1]
        assert not stderr and len(result['figures']) == 2
        assert_figures(page, result['figures'])
        assert set(model['labels']) == {0, 1} and len(model['labels']) == 72
        assert 'Группа 2' in public and 'Группа 3' not in public
        assert max_delta(model['input'], records['tsne'][0]['input']) == 0
        assert records['tsne'][0]['points'] == originals['ru'][1]['tsne'][0]['points']
        report['worker'].append({'language': 'ru', 'clusters': 2, 'perplexity': 15,
            'figures': 2, 'groups': 2})
        print('PASS edited CLUSTERS=2: two figures, same original-space colors', flush=True)

        stdout, stderr, result = run_worker(page,
            observed_source(source('10', 'experiments.py')), 'ru', '10', topic_count=5)
        public, records = diagnostic(stdout)
        assert not public.strip() and not stderr, (public, stderr)
        experiment = result['experiment']
        assert experiment['topics'][:4] == expected['topics'][:4]
        assert len(experiment['topics'][4]) == len(records['tsne']) == 3
        kmeans = [item for item in records['kmeans'] if item['clusters'] == 3][-1]
        labels = kmeans['labels']
        for perplexity, record, case in zip((5, 15, 30), records['tsne'], experiment['topics'][4]):
            check_projection(record, perplexity)
            assert max_delta(kmeans['input'], record['input']) == 0
            assert sum(len(series['points']) for series in case['series']) == 72
            assert 'до 500 итераций' in case['note']['ru']
            assert '500 итерацияға дейін' in case['note']['kk']
            for group, series in enumerate(case['series']):
                assert series['label'] == experiment['topics'][2][1]['series'][group]['label']
                actual = [point for point, label in zip(record['points'], labels) if label == group]
                assert series['points'] == [[round(float(x), 4), round(float(y), 4)] for x, y in actual]
            frozen = expected['topics'][4][(5, 15, 30).index(perplexity)]
            report['nativeComparison'][f'detailedPointsMaxDelta{perplexity}'] = max(
                max_delta(left['points'], right['points'])
                for left, right in zip(case['series'], frozen['series']))
        report['worker'].append({'kind': 'detailed', 'topics': 5,
            'fitSeconds': [item['seconds'] for item in records['tsne']]})
        print('PASS detailed t-SNE three conditions, same original-space KMeans colors, prior four topics unchanged', flush=True)
        print('Native/browser coordinate comparison: ' + json.dumps(report['nativeComparison']), flush=True)
        page.evaluate('window.qaWorker.terminate()')

        for language in ('ru', 'kk'):
            for width, height in ((1280, 900), (390, 844)):
                page.set_viewport_size({'width': width, 'height': height})
                open_editor(page, url, '10', language)
                static_topic = page.locator('#ml-topic-5')
                expect(static_topic.locator('h2')).to_contain_text('t-SNE')
                equal_units(static_topic.locator('svg'), expected['topics'][4][0])
                output = run_ui(page)
                assert 't-SNE' in output and '"topics"' not in output
                images = page.locator('.ml-python-figures img')
                expect(images).to_have_count(2)
                for image in images.all():
                    image.evaluate('image => image.decode()')
                frame = page.locator('.ml-python-figures figure').nth(1)
                frame.screenshot(path=str(ARTIFACTS / f'tsne-{language}-{width}.png'))
                zoom = page.locator('.ml-python-zoom').nth(1)
                zoom.click()
                expect(zoom).to_have_attribute('aria-pressed', 'true')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                frame.screenshot(path=str(ARTIFACTS / f'tsne-zoom-{language}-{width}.png'))
                zoom.click()
                page.locator('#ml-python-source').select_option('ml/10/experiments.py')
                expect(page.locator('#ml-python-status')).to_have_attribute('data-state', 'ready')
                detailed = run_ui(page)
                assert '"topics"' not in detailed
                topic = page.locator('#ml-python-topic')
                expect(topic.locator('option')).to_have_count(5)
                topic.select_option('4')
                expect(page.locator('#ml-python-experiment svg')).to_have_count(1)
                for case_index in range(3):
                    page.locator('#ml-python-case').select_option(str(case_index))
                    assert 'perplexity' in page.locator('#ml-python-experiment figcaption').inner_text().lower()
                    equal_units(page.locator('#ml-python-experiment svg'), experiment['topics'][4][case_index])
                page.locator('#ml-python-experiment figure').screenshot(
                    path=str(ARTIFACTS / f'detailed-{language}-{width}.png'))
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                if width == 390:
                    page.locator('#ml-python-source').select_option('ml/10/lab.py')
                    expect(page.locator('#ml-python-status')).to_have_attribute('data-state', 'ready')
                    failure = run_ui(page, edited_perplexity(code, 72), 'error')
                    assert 'ValueError' in failure and 'PERPLEXITY' in failure
                    localized = ('должна быть больше 0 и меньше 72' if language == 'ru'
                                 else '0-ден үлкен, 72 мәнінен кіші болуы керек')
                    assert localized in failure, failure
                    assert 't-SNE' in run_ui(page, code)
                report['ui'].append({'language': language, 'width': width,
                    'figures': 2, 'tsneCases': 3, 'overflow': False})
                print(f'PASS UI {language} {width}px: PCA+t-SNE PNGs, zoom, fifth topic and three conditions', flush=True)
        assert not errors, errors
        browser.close()
    if server:
        server.shutdown()
    (ARTIFACTS / 'browser-results.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('PASS practice 10 t-SNE: real Pyodide, edits, RU/KK, deterministic repeat and desktop/mobile', flush=True)


if __name__ == '__main__':
    main()
