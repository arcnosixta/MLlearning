"""Course payloads load on demand; an unavailable optional course cannot block others."""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_ready import goto_ready

URL = sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
with sync_playwright() as p:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page=browser.new_page(reduced_motion='reduce')
    requests=[]
    page.on('request', lambda request: requests.append(request.url))
    page.route('**/java-full/index.json', lambda route: route.abort())
    goto_ready(page,URL+'/?lang=ru')
    assert page.locator('.sysadmin-full-link').count()==1
    assert page.locator('.teaching-card-link').count()>0
    assert not any('/java-full/catalog.json' in url or '/sysadmin-full/catalog.json' in url for url in requests)
    page.unroute('**/java-full/index.json')
    requests.clear()
    goto_ready(page,URL+'/?lang=ru#sysadmin/topic/014')
    assert page.locator('.sysadmin-full-article').count()==1
    assert any('/sysadmin-full/guides/08.json' in url for url in requests)
    assert not any('/teaching.json' in url or '/java-full/' in url for url in requests)
    page.route('**/java-full/01/chapter.json', lambda route: route.abort())
    goto_ready(page,URL+'/?lang=ru#java/topic/01')
    assert page.locator('#full-course-retry').count()==1
    page.unroute('**/java-full/01/chapter.json')
    page.locator('#full-course-retry').click()
    page.locator('.java-full-article').wait_for()
    browser.close()
print('PASS isolated optional failures, lazy topic payloads and explicit retry')
