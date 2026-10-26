"""Exercise complete reading, bilingual navigation, persistence and mobile layout."""
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_ready import goto_ready

ROOT = Path(__file__).resolve().parents[1]
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
chapters = json.loads((ROOT / 'dist/java-full/catalog.json').read_text(encoding='utf-8'))
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for lang in ['ru', 'kk']:
        goto_ready(page, URL + '/?lang=' + lang + '#java/full')
        assert page.locator('.java-full .week-card').count() == 26
        for chapter in chapters:
            goto_ready(page, URL + '/?lang=' + lang + '#java/topic/' + chapter['id'])
            assert page.locator('.java-full-article h1').inner_text() == chapter[lang]['title']
            assert page.locator('[data-full-answer]').count() == 3
            assert page.locator('.java-full-content details').count() == 3
            assert page.locator('.java-full-content pre').count() >= 2
            download = page.locator('a[download]').first.get_attribute('href')
            assert page.request.get(URL + '/' + download).text() == chapter['code']
        print('PASS all 26 chapter pages and downloads', lang, flush=True)
    goto_ready(page, URL + '/?lang=ru#java/topic/01')
    unsafe = '<script>window.injected=1</script> мой ответ'
    page.locator('[data-full-answer]').nth(0).fill(unsafe)
    page.locator('[data-full-answer]').nth(2).fill('independent third answer')
    page.locator('#java-full-complete').click()
    page.reload()
    page.locator('[data-full-answer]').first.wait_for()
    assert page.locator('[data-full-answer]').first.input_value() == unsafe
    assert page.evaluate('window.injected === undefined')
    goto_ready(page, URL + '/?lang=kk#java/topic/01')
    assert page.locator('[data-full-answer]').first.input_value() == unsafe
    assert page.locator('[data-full-answer]').nth(2).input_value() == 'independent third answer'
    assert page.evaluate("()=>{const raw=MLStore.export();MLStore.clear();MLStore.import(raw);return MLStore.get().learning.completed.includes('java-full/01')}")
    assert page.evaluate("()=>{const raw=MLStore.export(),bad=JSON.parse(raw);bad.learning.practice['java-full/27/1']='invalid';try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===raw}}")
    assert page.evaluate("()=>{const raw=MLStore.export(),bad=JSON.parse(raw);bad.learning.practice['java-full/01/4']='invalid';try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===raw}}")
    # Actual navigation and continuation from the landing page.
    goto_ready(page, URL + '/?lang=ru')
    assert page.locator('.java-full-link').count() == 2
    assert page.locator('.studio-hero .button.outline').get_attribute('href') == '#java/topic/01'
    page.locator('[data-course-id="java"] .java-full-link').click()
    page.wait_for_function("location.hash==='#java/full' && document.querySelector('main').dataset.route===location.hash")
    page.locator('.week-card').first.click()
    page.wait_for_function("document.querySelector('main').dataset.route===location.hash")
    assert page.locator('.java-full-article').count() == 1
    for route in ['#java', '#java/week/01', '#java/week/14', '#track/java-advanced', '#track/java-advanced/01', '#progress']:
        goto_ready(page, URL + '/?lang=ru' + route)
        assert page.locator('.java-full-links,.java-full-banner').count() == 1, route
    goto_ready(page, URL + '/?lang=ru#java/topic/25')
    lab = page.locator('a[download][href$="lab.zip"]').get_attribute('href')
    assert page.request.get(URL + '/' + lab).body().startswith(b'PK')
    # A wrong topic has a recoverable destination.
    goto_ready(page, URL + '/?lang=ru#java/topic/99')
    assert page.locator('main a[href="#java/full"]').count() == 1
    for lang in ['ru', 'kk']:
        for width in [320, 390, 768]:
            page.set_viewport_size({'width': width, 'height': 844})
            for route in ['#java/full', '#java/topic/01', '#java/topic/20', '#java/topic/25']:
                goto_ready(page, URL + '/?lang=' + lang + route)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (lang, width, route)
        print('PASS responsive reading', lang, flush=True)
    page.set_viewport_size({'width': 390, 'height': 844})
    goto_ready(page, URL + '/?lang=kk#java/topic/01')
    page.screenshot(path=str(ROOT / 'artifacts/java-full-mobile.png'))
    assert not errors, errors
    browser.close()
print('PASS full-course persistence, export/import, continuation and mobile reading')
