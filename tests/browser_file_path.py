import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
catalog=json.loads((ROOT/'dist/file-course.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    for lang in ['ru','kk']:
        page.goto(url+'/?lang='+lang+'#course')
        page.locator('.pathway-card').first.wait_for()
        assert page.locator('.pathway-card').count()==2
        page.locator('.pathway-card[href="#files"]').click()
        page.locator('.file-card').first.wait_for()
        assert page.locator('.file-card').count()==7
        page.locator('#file-search').fill('Pipeline')
        assert page.locator('.file-card').count()==1
        page.locator('#file-search').fill('')
        for item in catalog:
            page.goto(url+'/?lang='+lang+'#files/'+item['id'])
            page.locator('#file-complete').wait_for()
            assert page.locator('.file-lesson h1').first.inner_text()==item[lang]['title']
            assert page.locator('[data-source-cell]').count()==item['cellCount']
            assert page.locator('[data-copy-cell]').count()==item['codeCount']
            page.locator(f'[data-file-answer="{item[lang]["quiz"]["answer"]}"]').click()
            assert page.locator('.quiz-result').inner_text().startswith('Дұрыс!' if lang=='kk' else 'Верно!')
            assert page.locator('a[download]').get_attribute('href')==item['download']
        page.goto(url+'/?lang='+lang+'#files')
        page.locator('.file-card').first.wait_for()
        page.screenshot(path=str(ROOT/'artifacts'/f'file-path-{lang}.png'),full_page=True)
    # Both pathways may have lesson 01, but their records must be independent.
    page.goto(url+'/?lang=ru#lesson/01')
    page.locator('#lesson-note').fill('Main pathway note')
    page.locator('#complete').click()
    page.goto(url+'/?lang=ru#files/01')
    page.locator('#file-note').fill('File pathway note')
    page.locator('#file-complete').click()
    page.reload();page.locator('#file-note').wait_for()
    assert page.locator('#file-note').input_value()=='File pathway note'
    assert page.evaluate('MLStore.get().notes["01"]')=='Main pathway note'
    assert page.evaluate('MLStore.get().files.completed')==['01']
    assert page.evaluate('MLStore.get().completed')==['01']
    assert page.locator('#file-complete').inner_text()=='Пройдено ✓'
    assert page.evaluate('JSON.parse(MLStore.export()).files.notes["01"]')=='File pathway note'
    # Old backups remain readable; bad new file IDs must be rejected atomically.
    assert page.evaluate("()=>{const current=MLStore.export();const older=JSON.parse(current);delete older.files;MLStore.import(JSON.stringify(older));const ok=MLStore.get().files.completed.length===0&&MLStore.get().completed[0]==='01';MLStore.import(current);return ok}")
    assert page.evaluate("()=>{const before=MLStore.export();const bad=JSON.parse(before);bad.files.completed=['99'];try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===before}}")
    page.set_viewport_size({'width':390,'height':844})
    for route in ['#files','#files/02','#files/06','#course']:
        page.goto(url+'/?lang=kk'+route)
        page.locator('.file-card' if route=='#files' else '#file-complete' if route.startswith('#files/') else '.pathway-card').first.wait_for()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),route
    page.goto(url+'/?lang=kk#files/06');page.locator('#file-complete').wait_for()
    page.locator('.saved-output').first.locator('summary').click()
    assert page.locator('.notebook img').count()>0
    page.screenshot(path=str(ROOT/'artifacts/file-lesson-mobile.png'),full_page=True)
    assert not errors,errors
    browser.close()
print('PASS two pathways, 14 localized file pages, search, all 401 cells, independent persistence and mobile')
