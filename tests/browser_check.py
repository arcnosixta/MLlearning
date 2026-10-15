"""Browser smoke tests. Run against a served dist directory."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
out = Path(__file__).resolve().parents[1]/'artifacts'
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    import os
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(viewport={'width':1440,'height':1100}, device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(url+'/#course')
    page.locator('.module-card').first.wait_for()
    assert page.locator('.module-card').count()==6
    page.screenshot(path=str(out/'desktop.png'),full_page=True)
    page.get_by_role('searchbox').fill('PCA')
    assert page.locator('.module-card').count()==1
    page.locator('.module-card').click()
    page.get_by_role('heading',name='PCA: сжимаем пространство признаков',exact=True).wait_for()
    for i in range(1,25):
        page.goto(f'{url}/#lesson/{i:02d}')
        page.locator('.lesson-body h1').wait_for()
        assert page.locator('pre code').inner_text().strip()
        assert page.locator('[data-answer]').count()==3
    page.goto(f'{url}/#lesson/01')
    page.get_by_role('button',name='Регрессия',exact=True).click()
    assert 'Верно!' in page.locator('.quiz-result').inner_text()
    page.locator('#complete').click()
    page.reload()
    page.get_by_role('button',name='Пройдено ✓',exact=True).wait_for()
    page.goto(f'{url}/#lab')
    page.locator('#mse').wait_for()
    before=float(page.locator('#mse').inner_text().split()[1])
    page.locator('#fit').click()
    after=float(page.locator('#mse').inner_text().split()[1])
    assert after<before
    page.locator('[data-lab="scaling"]').click()
    page.locator('#scale-mode').select_option('standard')
    assert 'равно 0' in page.locator('#scale-info').inner_text()
    page.locator('[data-lab="knn"]').click()
    assert 'Класс' in page.locator('#class-result').inner_text()
    page.locator('#k').fill('7')
    assert page.locator('#k-out').inner_text()=='7'
    page.screenshot(path=str(out/'lab.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    for route in ['#course', '#lesson/09', '#lab']:
        page.goto(url+'/'+route)
        if route=='#course':page.locator('.module-card').first.wait_for()
        elif 'lesson' in route:page.locator('.lesson-body h1').wait_for()
        else:page.locator('#class-result').wait_for()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), route
    page.goto(url+'/#course')
    page.locator('.module-card').first.wait_for()
    page.screenshot(path=str(out/'mobile.png'),full_page=True)
    assert not errors,errors
    browser.close()
print('PASS desktop/mobile, 24 lesson routes, quiz, progress, search and 3 experiments')
