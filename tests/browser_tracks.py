import json,os,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
tracks=json.loads((ROOT/'dist/tracks.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.on('dialog',lambda d:d.accept());errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    for lang in ['ru','kk']:
        page.goto(url+'/?lang='+lang);page.locator('.library-card').first.wait_for()
        assert page.locator('.library-card').count()==6
        page.locator('#library-search').fill('Go');assert page.locator('.library-card').count()==1
        page.locator('#library-search').fill('zzunknown');assert page.locator('.library-empty').count()==1
        page.locator('#library-search').fill('')
        page.locator('[data-library-filter="applied"]').click();assert page.locator('.library-card').count()==3
        for track in tracks:
            course=track['id'];page.goto(url+'/?lang='+lang+'#track/'+course)
            page.locator('.track-module').first.wait_for();assert page.locator('.track-module').count()==6
            for lesson in track['lessons']:
                page.goto(url+'/?lang='+lang+'#track/'+course+'/'+lesson['id'])
                page.locator('#track-complete').wait_for()
                assert page.locator('.track-lesson h1').inner_text()==lesson[lang]['title']
                assert page.locator('.java-section').count()==3
                assert page.locator('.track-quiz').count()==5
                q=lesson['questions'][0]
                page.locator(f'[data-track-q="{q["id"]}"] [data-track-answer="{q["answer"]}"]').click()
                assert page.locator(f'[data-track-q="{q["id"]}"] .java-feedback').inner_text().startswith('Верно!' if lang=='ru' else 'Дұрыс!')
                page.locator('#track-input').fill(lesson['terminal']['answers'][0])
                page.locator('#track-terminal button[type=submit]').click()
                assert page.locator('#track-terminal-result').get_attribute('data-correct')=='true'
                assert page.locator('a[download]').get_attribute('href').endswith(track['filename'])
    # Same lesson ID across courses must not share notes or completion.
    for track in tracks:
        course=track['id'];page.goto(url+'/?lang=ru#track/'+course+'/01')
        page.locator('#track-note').fill(course+' note');page.locator('#track-complete').click()
    page.reload();page.locator('#track-note').wait_for();assert page.locator('#track-note').input_value()=='sysadmin note'
    state=page.evaluate('MLStore.get().tracks');assert all(t['notes']['01']==course+' note' for course,t in state.items())
    assert page.evaluate("()=>{const before=MLStore.export();const old=JSON.parse(before);delete old.tracks;MLStore.import(JSON.stringify(old));const ok=MLStore.get().tracks.go.completed.length===0;MLStore.import(before);return ok}")
    assert page.evaluate("()=>{const before=MLStore.export(),bad=JSON.parse(before);bad.tracks.go.quiz['onec-01-q1']=0;try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===before}}")
    for track in tracks:
        course=track['id'];page.goto(url+'/?lang=ru#track/'+course+'/exam/mid')
        page.locator('#track-exam-start').click();page.locator('#track-exam-submit').wait_for()
        assert page.locator('.exam-question').count()==15
        first=page.locator('.exam-question input').first;first.check();name=first.get_attribute('name')
        page.reload();page.locator('#track-exam-submit').wait_for();assert page.locator(f'input[name="{name}"]').first.is_checked()
        page.locator('#track-exam-submit').click();page.locator('.track-result').wait_for();assert page.locator('.exam-review').count()==15
    # One full correct attempt and one expired attempt verify shared lifecycle.
    page.goto(url+'/?lang=kk#track/go/exam/final');page.locator('#track-exam-start').click();page.locator('#track-exam-submit').wait_for()
    assert page.locator('.exam-question').count()==30
    bank={q['id']:q['answer'] for lesson in tracks[0]['lessons'] for q in lesson['questions']}
    for qid in page.evaluate('MLStore.get().tracks.go.active.questionIds'):
        page.locator(f'input[name="{qid}"][value="{bank[qid]}"]').check()
    page.locator('#track-exam-submit').click();page.locator('.track-result').wait_for();assert '100%' in page.locator('.track-result').inner_text()
    page.goto(url+'/?lang=ru#track/sysadmin/exam/final');page.locator('#track-exam-start').click();page.locator('#track-exam-submit').wait_for()
    page.evaluate("()=>{const t=MLStore.get().tracks.sysadmin.active;t.startedAt=Date.now()-41*60000;t.deadline=t.startedAt+40*60000;MLStore.trackUpdate('sysadmin',{active:t})}")
    page.reload();page.locator('.track-result').wait_for();assert '0 / 30' in page.locator('.track-result').inner_text()
    page.set_viewport_size({'width':390,'height':844})
    for route in ['', '#track/go','#track/onec/04','#track/java-advanced/04','#track/sysadmin/05','#track/go/exam/final']:
        page.goto(url+'/?lang=kk'+route)
        selector='.library-card' if not route else '#track-exam-start' if '/exam/' in route else '#track-complete' if len(route.split('/'))==3 else '.track-module'
        page.locator(selector).first.wait_for();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),route
    page.goto(url+'/?lang=ru');page.locator('.library-card').first.wait_for();page.set_viewport_size({'width':1440,'height':1000});page.screenshot(path=str(ROOT/'artifacts/library-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT/'artifacts/library-mobile.png'),full_page=True)
    assert not errors,errors;browser.close()
print('PASS 48 bilingual modules, library search/filters, independent records, timed controls and mobile')
