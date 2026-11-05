"""Real Pyodide regression: 14 beginner examples, edits, RU/KK and chart protocol.

Run after scripts/build.py. Starts its own local HTTP server when URL is omitted.
PLAYWRIGHT_CHANNEL=msedge selects installed Edge on Windows.
"""
import base64
import functools
import http.server
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from browser_ready import goto_ready

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'artifacts/ml-qa'
ARTIFACTS.mkdir(parents=True, exist_ok=True)
EDIT = {
    '01': ('TRAIN_DAYS = 6', 'TRAIN_DAYS = 5'),
    '02': ('6,A,1700', '6,A,2700'),
    '03': ('9, 24],', '9, 14],'),
    '04': ('SimpleImputer(strategy="median")', 'SimpleImputer(strategy="mean")'),
    '05': ('SEED = 12', 'SEED = 17'),
    '06': ('THRESHOLD = 0.5', 'THRESHOLD = 0.7'),
    '07': ('THRESHOLD = 0.5', 'THRESHOLD = 0.7'),
    '08': ('NEIGHBORS = 5', 'NEIGHBORS = 1'),
    '09': ('MAX_DEPTH = 3', 'MAX_DEPTH = 10'),
    '10': ('CLUSTERS = 3', 'CLUSTERS = 2'),
    '11': ('C_VALUES = [0.1, 1.0, 10.0]', 'C_VALUES = [0.01, 0.1, 1.0]'),
    '12': ('EPOCHS = 400', 'EPOCHS = 40'),
    '13': ('DIRECTION = "vertical"', 'DIRECTION = "horizontal"'),
    '14': ('IOU_THRESHOLD = 0.5', 'IOU_THRESHOLD = 0.8'),
}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def source(week, name='lab.py'):
    return (ROOT / 'dist/ml' / week / name).read_text(encoding='utf-8')


def run_worker(page, code, language='ru', week=None, expected='result', topic_count=None):
    args = {'code': code, 'language': language}
    if week and (ROOT / 'dist/ml' / week / 'data.csv').is_file():
        args['dataset'] = {'name': 'data.csv', 'text': source(week, 'data.csv')}
    if topic_count is not None:
        args['topicCount'] = topic_count
    result = page.evaluate('''args => new Promise((resolve, reject) => {
      const worker = window.qaWorker, id = ++window.qaId, messages = [];
      const timer = setTimeout(() => reject(new Error('Python worker timed out')), 180000);
      worker.onmessage = ({data}) => {
        if(data.id !== id) return;
        messages.push(data);
        if(['result', 'error'].includes(data.type)) {
          clearTimeout(timer); resolve({messages});
        }
      };
      worker.onerror = event => {clearTimeout(timer); reject(new Error(event.message));};
      worker.postMessage({type:'run', id, ...args});
    })''', args)
    messages = result['messages']
    final = messages[-1]
    stdout = ''.join(m.get('text', '') for m in messages if m.get('stream') == 'stdout')
    stderr = ''.join(m.get('text', '') for m in messages if m.get('stream') == 'stderr')
    assert final['type'] == expected, (week, language, final, stdout, stderr)
    return stdout, stderr, final


def assert_figures(page, figures):
    assert 1 <= len(figures) <= 4
    for png in figures:
        assert base64.b64decode(png).startswith(b'\x89PNG\r\n\x1a\n')
        assert page.evaluate('''async png => {
          const image = new Image(); image.src = 'data:image/png;base64,' + png;
          await image.decode(); return image.naturalWidth > 0 && image.naturalHeight > 0;
        }''', png)


def open_editor(page, url, week, language):
    # A same-URL goto is a same-document navigation and retains the previous editor.
    page.goto('about:blank')
    goto_ready(page, f'{url}/?lang={language}#course/week/{week}')
    page.locator('details.ml-code > summary').click()
    expect(page.locator('#ml-python-status')).to_have_attribute('data-state', 'ready')


def run_ui(page, code=None, state='success'):
    if code is not None:
        page.locator('#ml-python-editor').fill(code)
    page.locator('#ml-python-run').click()
    expect(page.locator('#ml-python-status')).to_have_attribute(
        'data-state', re.compile(r'^(success|error|stopped)$'), timeout=180000)
    assert page.locator('#ml-python-status').get_attribute('data-state') == state, page.locator('#ml-python-output').inner_text()
    return page.locator('#ml-python-output').inner_text()


def main():
    server = None
    if len(sys.argv) > 1:
        url = sys.argv[1].rstrip('/')
    else:
        handler = functools.partial(QuietHandler, directory=str(ROOT / 'dist'))
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}'
    report = {'worker': [], 'ui': []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
        page = browser.new_page(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        goto_ready(page, f'{url}/?lang=ru#course')
        page.evaluate("window.qaId = 0; window.qaWorker = new Worker('ml/python-worker.js', {type:'module'});")
        for week, (before, after) in EDIT.items():
            code = source(week)
            assert before in code, (week, before)
            outputs = {}
            original_results = {}
            for language in ('ru', 'kk'):
                start = time.monotonic()
                stdout, stderr, result = run_worker(page, code, language, week)
                assert stdout.strip() and len(stdout) < 5000, (week, stdout)
                assert not stderr, (week, stderr)
                assert '"topics"' not in stdout and 'JsProxy' not in stdout
                assert not result.get('experiment')
                assert_figures(page, result['figures'])
                outputs[language] = stdout
                original_results[language] = result
                report['worker'].append({'week': week, 'language': language, 'kind': 'beginner', 'stdoutChars': len(stdout), 'figures': len(result['figures']), 'seconds': round(time.monotonic() - start, 2)})
            assert outputs['ru'] != outputs['kk'], week
            edited = code.replace(before, after, 1)
            for language in ('ru', 'kk'):
                stdout, stderr, result = run_worker(page, edited, language, week)
                assert not stderr, (week, stderr)
                assert_figures(page, result['figures'])
                assert stdout != outputs[language] or result['figures'] != original_results[language]['figures'], (week, 'Edit had no observable effect')
                report['worker'].append({'week': week, 'language': language, 'kind': 'edited', 'edit': after, 'figures': len(result['figures'])})
            lesson = json.loads(source(week, 'lesson.json'))
            count = len(lesson['ru']['topics'])
            stdout, stderr, result = run_worker(page, source(week, 'experiments.py'), 'ru', week, topic_count=count)
            assert not stdout.strip() and not stderr, (week, stdout, stderr)
            assert result.get('experiment') == json.loads(source(week, 'results.json')), week
            report['worker'].append({'week': week, 'kind': 'detailed', 'topics': count})
            print(f'PASS week {week}: RU/KK, edited example and all detailed charts in real Pyodide', flush=True)

        # Public print output is preserved; only a validated chart protocol is consumed.
        code = 'import json\nprint(json.dumps({"message": "математика", "topics": []}, ensure_ascii=False))\n'
        stdout, stderr, result = run_worker(page, code)
        assert json.loads(stdout)['message'] == 'математика' and not result.get('experiment')
        chart = json.loads(source('01', 'results.json'))
        code = 'import json\nprint("before chart")\nprint(json.dumps(' + repr(chart) + ', ensure_ascii=True, indent=2))\nprint("after chart")\n'
        stdout, stderr, result = run_worker(page, code, topic_count=len(chart['topics']))
        assert stdout == 'before chart\nafter chart\n' and result.get('experiment') == chart
        stdout, stderr, result = run_worker(page, 'print("before failure")\nraise ValueError("student error")\n', expected='error')
        assert 'before failure' in stdout and 'ValueError: student error' in result['message']
        stdout, stderr, result = run_worker(page, 'import warnings\nwarnings.warn("student warning", RuntimeWarning)\nprint("fresh run")\n')
        assert stdout == 'fresh run\n' and 'student warning' in stderr
        stdout, stderr, result = run_worker(page, 'print("clean second run")\n')
        assert stdout == 'clean second run\n' and not stderr and not result['figures']
        page.evaluate('window.qaWorker.terminate()')
        print('PASS chart JSON extraction, arbitrary JSON, Unicode, warning visibility and error/repeat cleanup', flush=True)

        for language in ('ru', 'kk'):
            for width, height in ((1280, 900), (390, 844)):
                page.set_viewport_size({'width': width, 'height': height})
                open_editor(page, url, '05', language)
                stdout = run_ui(page)
                assert '"topics"' not in stdout
                expect(page.locator('.ml-python-figures img')).to_have_count(1)
                page.locator('.ml-python-figures img').evaluate('image => image.decode()')
                page.locator('.ml-python-zoom').click()
                expect(page.locator('.ml-python-zoom')).to_have_attribute('aria-pressed', 'true')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (language, width, 'zoom')
                page.locator('.ml-python-figures').screenshot(path=str(ARTIFACTS / f'chart-zoom-{language}-{width}.png'))
                page.locator('.ml-python-zoom').click()
                expect(page.locator('.ml-python-zoom')).to_have_attribute('aria-pressed', 'false')
                page.locator('.ml-python-figures').screenshot(path=str(ARTIFACTS / f'chart-{language}-{width}.png'))
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (language, width)
                page.locator('#ml-python-output').scroll_into_view_if_needed()
                page.screenshot(path=str(ARTIFACTS / f'after-{language}-{width}.png'))
                report['ui'].append({'language': language, 'width': width, 'week': '05', 'stdoutChars': len(stdout)})
                # Switching sources must retain each editable draft independently.
                draft = source('05') + '\n# student draft\n'
                page.locator('#ml-python-editor').fill(draft)
                page.locator('#ml-python-source').select_option('ml/05/experiments.py')
                expect(page.locator('#ml-python-status')).to_have_attribute('data-state', 'ready')
                detailed = run_ui(page)
                assert '"topics"' not in detailed and detailed.strip()
                expect(page.locator('#ml-python-experiment')).to_be_visible()
                expect(page.locator('#ml-python-experiment svg')).to_have_count(1)
                page.locator('#ml-python-topic').select_option('1')
                page.locator('#ml-python-case').select_option('2')
                page.locator('#ml-python-source').select_option('ml/05/lab.py')
                expect(page.locator('#ml-python-status')).to_have_attribute('data-state', 'ready')
                expect(page.locator('#ml-python-editor')).to_have_value(draft)
                page.locator('#ml-python-reset').click()
                expect(page.locator('#ml-python-editor')).to_have_value(source('05'))
                output = run_ui(page, 'print("visible error context")\nraise ValueError("edited error")\n', 'error')
                assert 'visible error context' in output and 'ValueError: edited error' in output
                output = run_ui(page, 'print("retry succeeded")\n')
                assert output.strip() == 'retry succeeded'
                assert not page.locator('.ml-python-figures img').count()
                assert page.locator('#ml-python-experiment').is_hidden()
                print(f'PASS UI {language} {width}px: PNG, source drafts/reset, detailed charts, error/retry and overflow', flush=True)
        assert not errors, errors
        browser.close()
    if server:
        server.shutdown()
    (ARTIFACTS / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('PASS 14 editable beginner examples, 14 detailed protocols, both languages and desktop/mobile', flush=True)


if __name__ == '__main__':
    main()
