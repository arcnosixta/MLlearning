import json,os,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
items=json.loads((ROOT/'dist/teaching.json').read_text(encoding='utf-8'))
def parent(path,ident):return '#lesson/'+ident if path=='ml' else '#files/'+ident if path=='files' else '#java/week/'+ident if path=='java' else '#track/'+path+'/'+ident
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');page.on('dialog',lambda d:d.accept());errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    for lang in ['ru','kk']:
        for item in items:
            path,ident=item['path'],item['id']
            page.goto(url+'/?lang='+lang+'#learn/'+path+'/'+ident)
            page.locator('.teaching-guide').wait_for()
            assert page.locator('.teaching-page h1').inner_text()==item[lang]['title']
            assert page.locator('.teaching-exercise').count()==2
            assert page.locator('.teaching-glossary dt').count()>=2
            assert page.locator('.teaching-solution').count()==2
            if ident=='start':
                assert page.locator('a[download]').first.get_attribute('href').endswith(item['filename'])
                assert page.locator('a[download]').count()==1+len(item.get('attachments',[]))
            else:
                page.goto(url+'/?lang='+lang+parent(path,ident));page.locator('[data-teaching="'+path+'/'+ident+'"]').wait_for()
                assert page.locator('.teaching-guide').count()==1
        print('PASS all parent and standalone guides',lang,flush=True)
    # Two paths with the same topic ID must retain independent written solutions.
    for path in ['ml','go']:
        page.goto(url+'/?lang=kk#learn/'+path+'/01');page.locator('[data-learning-answer]').first.fill(path+' <script>alert(1)</script>')
        page.locator('[data-learning-complete]').click()
    page.reload();page.locator('[data-learning-answer]').first.wait_for();assert page.locator('[data-learning-answer]').first.input_value().startswith('go ')
    state=page.evaluate('MLStore.get().learning');assert state['practice']['ml/01/1'].startswith('ml ');assert 'go/01' in state['completed']
    assert page.evaluate("()=>{const raw=MLStore.export();const old=JSON.parse(raw);delete old.learning;MLStore.import(JSON.stringify(old));const ok=MLStore.get().learning.completed.length===0;MLStore.import(raw);return ok}")
    assert page.evaluate("()=>{const raw=MLStore.export(),bad=JSON.parse(raw);bad.learning.practice['go/14/1']='bad';try{MLStore.import(JSON.stringify(bad));return false}catch{return MLStore.export()===raw}}")
    page.goto(url+'/?lang=ru#lesson/01');page.locator('.teaching-guide').wait_for();page.locator('#complete').click();page.locator('.teaching-guide').wait_for();assert page.locator('.teaching-guide').count()==1
    page.set_viewport_size({'width':390,'height':844})
    for item in items:
        if item['id'] not in ['start','01']:continue
        page.goto(url+'/?lang=kk#learn/'+item['path']+'/'+item['id']);page.locator('.teaching-guide').wait_for()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),item['path']
    page.goto(url+'/?lang=kk');page.locator('.teaching-card-link').first.wait_for();assert page.locator('.teaching-card-link').count()==6
    page.goto(url+'/?lang=ru#learn/ml/start');page.locator('.teaching-guide').wait_for();page.screenshot(path=str(ROOT/'artifacts/teaching-mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000});page.screenshot(path=str(ROOT/'artifacts/teaching-desktop.png'),full_page=True)
    assert not errors,errors
    # Additional material failing to load must not replace a functioning core lesson.
    fallback=browser.new_context()
    fallback.route('**/teaching.json',lambda route:route.abort())
    offline=fallback.new_page();offline.goto(url+'/?lang=ru#lesson/01')
    offline.locator('#complete').wait_for();offline.locator('#toast.show').wait_for()
    assert offline.locator('.lesson-body h1').inner_text()
    fallback.close()
    browser.close()
print('PASS teaching routes, bilingual coverage, migration, written practice, re-render and mobile')
