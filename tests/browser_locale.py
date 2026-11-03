"""Verify the new bilingual ML routes, charts, downloads and network isolation."""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from browser_ready import goto_ready

ROOT = Path(__file__).resolve().parents[1]
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
ids = [f'{n:02d}' for n in range(1, 15)]
with sync_playwright() as p:
    browser = p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    context = browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce', accept_downloads=True)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for lang in ('ru', 'kk'):
        goto_ready(page, f'{URL}/?lang={lang}#course')
        assert page.locator('html').get_attribute('lang') == lang
        assert page.locator('.ml-weeks li').count() == 14
        page.locator('#ml-search').fill('YOLO')
        assert page.locator('.ml-weeks li').count() == 1
        assert page.locator('.ml-weeks h2 a').get_attribute('href') == '#course/week/14'
        for ident in [*ids, 'project']:
            section = 'project' if ident == 'project' else f'week/{ident}'
            goto_ready(page, f'{URL}/?lang={lang}#course/{section}')
            folder = ROOT / 'dist/ml' / ident
            content = json.loads((folder / 'lesson.json').read_text(encoding='utf-8'))[lang]
            results = json.loads((folder / 'results.json').read_text(encoding='utf-8'))['topics']
            assert page.locator('.ml-reader h1').inner_text() == content['title']
            assert page.locator('svg.ml-plot').count() == len(content['topics'])
            for n, topic in enumerate(content['topics']):
                lab = page.locator('.ml-lab').nth(n)
                plot = lab.locator('svg')
                original = plot.get_attribute('aria-label')
                lab.locator('select').select_option('1')
                assert plot.get_attribute('aria-label') != original
                assert lab.locator('figcaption').inner_text().startswith(results[n][1]['note'][lang])
                quiz = page.locator('.ml-quiz').nth(n)
                quiz.locator(f'[data-answer="{topic["answer"]}"]').click()
                assert quiz.locator('.ml-feedback').get_attribute('data-correct') == 'true'
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (lang, ident)
        print(f'PASS all ML sections and interactive plots in {lang}', flush=True)
    goto_ready(page, f'{URL}/?lang=kk#course/week/01')
    page.locator('.ml-points summary').first.click()
    assert page.locator('.ml-table tbody tr').first.is_visible()
    page.locator('.ml-code summary').click()
    page.locator('.ml-code code').get_by_text('import', exact=False).wait_for()
    with page.expect_download() as pending:
        page.locator('a[download][href$="lab.zip"]').click()
    assert pending.value.suggested_filename == 'lab.zip'
    page.locator('.language-switch a[lang="ru"]').click()
    page.wait_for_url('**/?lang=ru#course/week/01')
    page.locator('.ml-reader h1').wait_for()
    assert page.locator('html').get_attribute('lang') == 'ru'
    goto_ready(page, f'{URL}/#course/labs')
    assert page.locator('.ml-weeks a[download]').count() == 14
    for retired in ('#lesson/24', '#files/07', '#learn/ml/01'):
        goto_ready(page, f'{URL}/{retired}')
        assert page.locator('.ml-course .callout').is_visible()
    assert not errors, errors
    context.close()

    # ML fetches only on ML routes, and a failed result can be retried.
    isolated = browser.new_context(reduced_motion='reduce')
    failures = []
    def fail_once(route):
        if not failures:
            failures.append(route.request.url)
            route.abort()
        else:
            route.continue_()

    isolated.route('**/ml/01/results.json', fail_once)
    other = isolated.new_page()
    goto_ready(other, f'{URL}/#java')
    assert other.locator('.week-card').count() and not failures
    goto_ready(other, f'{URL}/#course/week/01')
    other.locator('#full-course-retry').click()
    other.locator('.ml-reader h1').wait_for()
    assert len(failures) == 1
    isolated.close()
    browser.close()
print('PASS ML downloads, language switching, legacy routes and recoverable loading')
