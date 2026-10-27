"""Review scoring, backup validation and keyboard access must match the learner's actions."""
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_ready import goto_ready

ROOT=Path(__file__).resolve().parents[1]
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
questions=json.loads((ROOT/'dist/sysadmin-full/review.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(reduced_motion='reduce')
    page.route('https://www.youtube-nocookie.com/**',lambda route:route.fulfill(body='<p>player</p>',content_type='text/html'))
    goto_ready(page,URL+'/?lang=ru#sysadmin/review')
    assert page.evaluate("document.activeElement.tagName==='H1'")
    assert page.locator('.sysadmin-review').count()==35
    first=page.locator('[data-review="01"]')
    first.locator('input[value="'+str((questions[0]['answer']+1)%3)+'"]').check()
    first.locator('button').click()
    assert first.locator('[data-correct="false"]').count()==1
    for question in questions:
        form=page.locator('[data-review="'+question['id']+'"]')
        form.locator('input[value="'+str(question['answer'])+'"]').check()
        form.locator('button').click()
        assert form.locator('[data-correct="true"]').count()==1
    assert '35/35' in page.locator('#sysadmin-review-score').inner_text()
    assert page.evaluate('MLStore.get().learning.completed')==[]
    assert page.evaluate("()=>{const raw=MLStore.export();MLStore.clear();MLStore.import(raw);return Object.keys(MLStore.get().learning.review).length===35}")
    for key,value in [('sysadmin/36',0),('sysadmin/01',3),('sysadmin/01','1')]:
        assert page.evaluate("([key,value])=>{const raw=MLStore.export(),bad=JSON.parse(raw);bad.learning.review[key]=value;try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===raw}}",[key,value])
    goto_ready(page,URL+'/?lang=kk#sysadmin/topic/001')
    assert page.locator('.sysadmin-review input:checked').input_value()==str(questions[0]['answer'])
    assert page.locator('[data-correct="true"]').count()==1
    page.locator('#sysadmin-video-load').focus();page.keyboard.press('Enter')
    page.locator('.sysadmin-player iframe').wait_for()
    assert page.evaluate("document.activeElement.tagName==='IFRAME'")
    page.set_viewport_size({'width':320,'height':844})
    goto_ready(page,URL+'/?lang=kk#sysadmin/review')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    browser.close()
print('PASS all35 scenario scores, isolated progress, typed backup validation and keyboard focus')
