from browser_ready import goto_ready
import json,os,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
weeks=json.loads((ROOT/'dist/java-course.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('dialog',lambda dialog:dialog.accept())
    for lang in ['ru','kk']:
        goto_ready(page,url+'/?lang='+lang)
        page.locator('.campus-hero').wait_for()
        assert page.locator('.brand').first.inner_text().startswith('im\nIMlearning') or 'IMlearning' in page.locator('.brand').first.inner_text()
        goto_ready(page,url+'/?lang='+lang+'#java')
        page.locator('.week-card').first.wait_for();assert page.locator('.week-card').count()==14
        page.locator('[data-java-phase="first"]').click();assert page.locator('.week-card').count()==7
        for week in weeks:
            goto_ready(page,url+'/?lang='+lang+'#java/week/'+week['id'])
            page.locator('#java-complete').wait_for()
            assert page.locator('.java-lesson h1').inner_text()==week[lang]['title']
            assert page.locator('.java-section').count()==3
            assert page.locator('.java-quiz').count()==6
        goto_ready(page,url+'/?lang='+lang+'#java/week/07')
        page.locator('#terminal-input').fill('abstract int area();')
        page.locator('.terminal-box button[type=submit]').click()
        assert page.locator('.terminal-result').get_attribute('data-correct')=='true'
        page.locator('#java-note').fill('Java note '+lang)
        page.locator('#java-complete').click()
        page.reload();page.locator('#java-note').wait_for()
        assert page.locator('#java-note').input_value()=='Java note '+lang
    # Starting a 30-question checkpoint, persisted answers and result review.
    goto_ready(page,url+'/?lang=ru#exam/rk1');page.locator('#exam-start').click()
    page.locator('#exam-submit').wait_for();assert page.locator('.exam-question').count()==30
    first=page.locator('.exam-question').first.locator('input').first
    first.check();name=first.get_attribute('name');page.reload();page.locator('#exam-submit').wait_for()
    assert page.locator(f'input[name="{name}"]').first.is_checked()
    page.locator('#exam-submit').click();page.locator('.exam-result-score').wait_for()
    assert page.locator('.exam-review').count()==30
    assert '/30' in page.locator('.exam-result-score').inner_text().replace(' ','')
    # Session must contain 60 distinct questions and score all-correct accurately.
    goto_ready(page,url+'/?lang=ru#exam/session');page.locator('#exam-start').click()
    page.locator('#exam-submit').wait_for();assert page.locator('.exam-question').count()==60
    answers={q['id']:q['answer'] for week in weeks for q in week['questions']}
    ids=page.evaluate('MLStore.get().java.active.questionIds')
    for qid in ids:page.locator(f'input[name="{qid}"][value="{answers[qid]}"]').check()
    page.locator('#exam-submit').click();page.locator('.exam-result-score').wait_for()
    assert '100%' in page.locator('.exam-result-score').inner_text()
    # Expired attempt is submitted automatically upon returning, not reset.
    goto_ready(page,url+'/?lang=ru#exam/rk2');page.locator('#exam-start').click();page.locator('#exam-submit').wait_for()
    page.evaluate('()=>{const j=MLStore.get().java;const now=Date.now()-46*60000;j.active.startedAt=now;j.active.deadline=now+45*60000;MLStore.javaUpdate({active:j.active})}')
    page.reload();page.locator('.exam-result-score').wait_for();assert '0 / 30' in page.locator('.exam-result-score').inner_text()
    # Legacy backups retain ML data while introducing empty Java records.
    assert page.evaluate("()=>{const backup=MLStore.export(),old=JSON.parse(backup);delete old.java;MLStore.import(JSON.stringify(old));const ok=MLStore.get().java.completed.length===0;MLStore.import(backup);return ok}")
    assert page.evaluate("()=>{const before=MLStore.export(),bad=JSON.parse(before);bad.java.completed=['99'];try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===before}}")
    page.set_viewport_size({'width':390,'height':844})
    for route in ['', '#java','#java/week/07','#exam/rk1','#exams','#course','#files']:
        goto_ready(page,url+'/?lang=kk'+route)
        selector='.campus-hero' if not route else '.week-card' if route=='#java' else '#java-complete' if '/week/' in route else '#exam-start' if route=='#exam/rk1' else '.exam-tile' if route=='#exams' else '.module-card' if route=='#course' else '.file-card'
        page.locator(selector).first.wait_for()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),route
    goto_ready(page,url+'/?lang=kk');page.locator('.campus-hero').wait_for();page.screenshot(path=str(ROOT/'artifacts/imlearning-mobile.png'),full_page=True)
    assert not errors,errors
    browser.close()
print('PASS bilingual 14-week Java, terminal, notes, exam resume/scoring/expiry and mobile')
