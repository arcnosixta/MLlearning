import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
root=Path(__file__).resolve().parents[1]
kk=json.loads((root/'dist/lessons.kk.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url+'/?lang=kk#course')
    page.locator('.module-card').first.wait_for()
    assert page.locator('html').get_attribute('lang')=='kk'
    assert page.get_by_role('link',name='Негіздерден бастау',exact=False).count()==1
    for lesson in kk:
        page.goto(url+'/?lang=kk#lesson/'+lesson['id'])
        page.locator('.lesson-body h1').wait_for()
        assert page.locator('.lesson-body h1').inner_text()==lesson['title']
        assert page.locator('.lesson-intro').inner_text()==lesson['intro']
        page.locator(f'[data-answer="{lesson["quiz"]["answer"]}"]').click()
        assert page.locator('.quiz-result').inner_text().startswith('Дұрыс!')
        assert '/kk/' in page.locator('a[download]').get_attribute('href')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.goto(url+'/?lang=kk#lab')
    page.locator('#fit').wait_for()
    for lab in ['scaling','knn','regression']:
        page.locator('[data-lab="'+lab+'"]').click()
        assert page.locator('svg').count()==1
    page.locator('.language-switch a[lang="ru"]').click()
    page.locator('#fit').wait_for()
    assert page.locator('html').get_attribute('lang')=='ru'
    assert page.locator('#fit').inner_text()=='Найти лучшие w и b'
    page.locator('.language-switch a[lang="kk"]').click()
    page.locator('#fit').wait_for()
    page.goto(url+'/#course')
    page.locator('.module-card').first.wait_for()
    assert page.locator('html').get_attribute('lang')=='kk'
    assert not errors,errors
    browser.close()
print('PASS Kazakh UI, 24 lessons/quizzes/downloads, 3 labs, mobile and language persistence')
