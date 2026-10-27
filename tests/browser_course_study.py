"""Real study journeys across history, language, progress and practice."""
import os
import sys
from playwright.sync_api import sync_playwright
from browser_ready import goto_ready

URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    goto_ready(page,URL+'/?lang=ru#sysadmin/full')
    page.locator('#sysadmin-full-search').fill('BIND')
    assert page.locator('.sysadmin-video-card').count()==5
    page.locator('.sysadmin-video-card').first.click()
    page.locator('.sysadmin-full-article').wait_for()
    page.go_back()
    page.locator('#sysadmin-full-search').wait_for()
    assert page.locator('#sysadmin-full-search').input_value()=='BIND'
    assert page.locator('.sysadmin-video-card').count()==5
    page.locator('.language-switch a[lang="kk"]').click()
    page.locator('html[lang="kk"]').wait_for()
    page.locator('#sysadmin-full-search').wait_for()
    assert page.locator('#sysadmin-full-search').input_value()=='BIND'
    page.reload();page.locator('#sysadmin-full-search').wait_for()
    assert page.locator('#sysadmin-full-search').input_value()=='BIND'
    goto_ready(page,URL+'/?lang=ru#java/full')
    page.locator('#java-full-search').fill('JDBC')
    assert page.locator('.week-card:visible').count()==1
    page.locator('.week-card:visible').click()
    page.locator('.java-full-article').wait_for()
    page.go_back();page.locator('#java-full-search').wait_for()
    assert page.locator('#java-full-search').input_value()=='JDBC'
    goto_ready(page,URL+'/?lang=ru#sysadmin/topic/001')
    page.locator('[data-sysadmin-answer]').first.fill('keep my work')
    button=page.locator('#sysadmin-full-complete');button.click();assert button.get_attribute('aria-pressed')=='true'
    page.locator('#sysadmin-practice-complete').click()
    button.click();assert button.get_attribute('aria-pressed')=='false'
    assert page.locator('[data-sysadmin-answer]').first.input_value()=='keep my work'
    assert page.evaluate("MLStore.get().learning.completed.includes('sysadmin-practice/01')")
    assert not page.evaluate("MLStore.get().learning.completed.includes('sysadmin-full/001')")
    page.evaluate('MLStore.import(MLStore.export())');page.reload();page.locator('#sysadmin-practice-complete').wait_for()
    assert page.locator('#sysadmin-practice-complete').get_attribute('aria-pressed')=='true'
    goto_ready(page,URL+'/?lang=ru#java/topic/01')
    button=page.locator('#java-full-complete');button.click();button.click()
    assert button.get_attribute('aria-pressed')=='false'
    browser.close()
print('PASS filters survive browser Back, reload and actual language switching')
