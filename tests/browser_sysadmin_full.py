"""Verify the full playlist reader, opt-in video loading and local learning data."""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from browser_ready import goto_ready

ROOT = Path(__file__).resolve().parents[1]
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
data = json.loads((ROOT / 'dist/sysadmin-full/catalog.json').read_text(encoding='utf-8'))
entries, groups = data['entries'], data['groups']
group_by_id = {group['id']: group for group in groups}
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    errors = []
    video_requests = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('request', lambda request: video_requests.append(request.url) if 'youtube-nocookie.com' in request.url else None)
    # Verify the intended iframe URL without depending on YouTube playback/network access.
    page.route('https://www.youtube-nocookie.com/**', lambda route: route.fulfill(status=200, content_type='text/html', body='<html><body>test player</body></html>'))
    for lang in ['ru', 'kk']:
        goto_ready(page, URL + '/?lang=' + lang + '#sysadmin/full')
        assert page.locator('.sysadmin-video-card').count() == 106
        assert page.locator('.sysadmin-video-card').first.get_attribute('data-video-id') == entries[0]['id']
        assert page.locator('.sysadmin-video-card').last.get_attribute('data-video-id') == entries[-1]['id']
        page.locator('#sysadmin-full-group').select_option(groups[0]['id'])
        assert page.locator('.sysadmin-video-card').count() == len(groups[0]['videoIds'])
        page.locator('#sysadmin-full-group').select_option('all')
        page.locator('#sysadmin-full-search').fill(entries[0]['title'])
        assert page.locator('.sysadmin-video-card').count() == 1
        page.locator('#sysadmin-full-search').fill('no-such-course-xyz')
        assert page.locator('.sysadmin-video-card').count() == 0
        # Every original video has a shareable page in both interface languages.
        for entry in entries:
            goto_ready(page, URL + '/?lang=' + lang + '#sysadmin/topic/' + entry['courseId'])
            # YouTube titles can contain repeated spaces; the DOM keeps them while
            # browsers collapse visual whitespace in innerText.
            assert page.locator('.sysadmin-full-article h1').text_content() == entry['title']
            assert page.locator('[data-sysadmin-answer]').count() == 3
            assert page.locator('.sysadmin-full-content details').count() == 3
            assert page.locator('.sysadmin-player iframe').count() == 0
            assert page.locator('#sysadmin-video-load').count() == 1
            assert page.locator('a[href="' + entry['url'] + '"]').count() == 1
        print('PASS all 106 original video pages and bilingual UI', lang, flush=True)
    assert not video_requests, video_requests
    goto_ready(page, URL + '/?lang=ru#sysadmin/topic/001')
    with page.expect_request('https://www.youtube-nocookie.com/embed/' + entries[0]['id'] + '*'):
        page.locator('#sysadmin-video-load').click()
    iframe = page.locator('.sysadmin-player iframe')
    assert '/embed/' + entries[0]['id'] + '?' in iframe.get_attribute('src')
    assert iframe.get_attribute('title') == entries[0]['title']
    assert iframe.get_attribute('allowfullscreen') is not None
    assert page.locator('#sysadmin-video-load').count() == 0
    assert video_requests
    unsafe = '<script>window.injected=1</script> мой ответ'
    page.locator('[data-sysadmin-answer]').first.fill(unsafe)
    page.locator('[data-sysadmin-answer]').nth(2).fill('third independent answer')
    page.locator('#sysadmin-full-complete').click()
    page.reload()
    page.locator('[data-sysadmin-answer]').first.wait_for()
    assert page.locator('[data-sysadmin-answer]').first.input_value() == unsafe
    assert page.locator('[data-sysadmin-answer]').nth(2).input_value() == 'third independent answer'
    assert page.evaluate('window.injected === undefined')
    goto_ready(page, URL + '/?lang=kk#sysadmin/topic/001')
    assert page.locator('[data-sysadmin-answer]').first.input_value() == unsafe
    goto_ready(page, URL + '/?lang=ru#sysadmin/topic/002')
    page.locator('[data-sysadmin-answer]').first.fill('second video answer')
    assert page.evaluate("MLStore.get().learning.practice['sysadmin-full/001/1']") == unsafe
    assert page.evaluate("()=>{const raw=MLStore.export();MLStore.clear();MLStore.import(raw);return MLStore.get().learning.completed.includes('sysadmin-full/001')}")
    assert page.evaluate("()=>{const raw=MLStore.export(),bad=JSON.parse(raw);bad.learning.practice['sysadmin-full/107/1']='bad';try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===raw}}")
    assert page.evaluate("()=>{const raw=MLStore.export(),bad=JSON.parse(raw);bad.learning.practice['sysadmin-full/001/4']='bad';try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===raw}}")
    page.evaluate("MLStore.trackUpdate('sysadmin',{completed:['01']})")
    assert page.evaluate("MLStore.get().tracks.sysadmin.completed") == ['01']
    assert page.evaluate("MLStore.get().learning.completed.filter(key=>key.startsWith('sysadmin-full/'))") == ['sysadmin-full/001']
    goto_ready(page, URL + '/?lang=ru#sysadmin/full')
    page.locator('#sysadmin-full-progress').select_option('done')
    assert page.locator('.sysadmin-video-card').count() == 1
    page.locator('#sysadmin-full-progress').select_option('todo')
    assert page.locator('.sysadmin-video-card').count() == 105
    for route in ['', '#track/sysadmin', '#track/sysadmin/01', '#track/sysadmin/13', '#progress']:
        goto_ready(page, URL + '/?lang=ru' + route)
        selector='.sysadmin-full-link' if route=='' else '.sysadmin-full-banner,.sysadmin-full-links'
        assert page.locator(selector).count() == 1, route
    goto_ready(page, URL + '/?lang=ru#sysadmin/topic/002')
    goto_ready(page, URL + '/?lang=ru')
    assert page.locator('.studio-hero .button.outline').get_attribute('href') == '#sysadmin/topic/002'
    for group in groups:
        first = next(entry for entry in entries if entry['guideId'] == group['id'])
        goto_ready(page, URL + '/?lang=ru#sysadmin/topic/' + first['courseId'])
        download = page.locator('a[download]').get_attribute('href')
        assert download == group['download']
        assert page.request.get(URL + '/' + download).text() == group['code']
    goto_ready(page, URL + '/?lang=ru#sysadmin/topic/999')
    assert page.locator('main a[href="#sysadmin/full"]').count() == 1
    for lang in ['ru', 'kk']:
        for width in [320, 390, 768]:
            page.set_viewport_size({'width': width, 'height': 844})
            for route in ['#sysadmin/full', '#sysadmin/topic/001', '#sysadmin/topic/090', '#sysadmin/topic/106']:
                goto_ready(page, URL + '/?lang=' + lang + route)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (lang, width, route)
        print('PASS responsive playlist reading', lang, flush=True)
    page.set_viewport_size({'width': 390, 'height': 844})
    goto_ready(page, URL + '/?lang=kk#sysadmin/topic/001')
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    page.screenshot(path=str(ROOT / 'artifacts/sysadmin-full-mobile.png'))
    assert not errors, errors
    browser.close()
print('PASS opt-in video embed, downloads, written practice, progress, backup and navigation')
