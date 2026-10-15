"""Exercise persistence, legacy migration, backups, rejection and storage failure."""
import json
import os
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
with sync_playwright() as p, tempfile.TemporaryDirectory() as temporary:
    browser=p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    context=browser.new_context(accept_downloads=True)
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.on('dialog',lambda dialog:dialog.accept())
    page.goto(url+'/#course')
    page.locator('.module-card').first.wait_for()
    page.evaluate("localStorage.clear(); localStorage.setItem('mllearning-progress','[\"01\"]')")
    page.reload()
    page.locator('.module-card').first.wait_for()
    assert page.evaluate('MLStore.get().completed')==['01']
    page.goto(url+'/#lesson/09')
    page.locator('#lesson-note').fill('Менің жазбам <script>alert(1)</script> — личная заметка')
    page.locator('[data-answer="0"]').click()
    page.locator('#complete').click()
    page.reload()
    page.locator('#lesson-note').wait_for()
    assert 'Менің жазбам' in page.locator('#lesson-note').input_value()
    assert page.locator('[data-answer="0"]').get_attribute('class')=='correct'
    assert page.locator('#complete').inner_text().strip()=='Пройдено ✓'
    page.goto(url+'/#lab')
    page.locator('#weight').fill('2')
    page.locator('[data-lab="scaling"]').click()
    page.locator('#scale-mode').select_option('standard')
    page.locator('#multiplier').fill('30')
    page.reload()
    page.locator('#scale-mode').wait_for()
    assert page.locator('#scale-mode').input_value()=='standard'
    assert page.locator('#multiplier').input_value()=='30'
    page.locator('[data-lab="regression"]').click()
    assert page.locator('#weight').input_value()=='2'
    page.goto(url+'/#data')
    page.locator('#export-data').wait_for()
    before=page.evaluate('MLStore.get()')
    with page.expect_download() as pending:page.locator('#export-data').click()
    backup=Path(temporary)/'backup.json';pending.value.save_as(backup)
    saved=json.loads(backup.read_text(encoding='utf-8'))
    assert saved['completed']==['01','09']
    page.locator('#clear-data').click()
    assert page.evaluate('MLStore.get().notes')=={}
    page.locator('#import-data').set_input_files(backup)
    page.get_by_text('Данные восстановлены',exact=True).wait_for()
    assert page.evaluate('MLStore.get().notes')==before['notes']
    invalid=Path(temporary)/'invalid.json';invalid.write_text('{"version":1,"completed":["99"]}',encoding='utf-8')
    page.locator('#import-data').set_input_files(invalid)
    page.get_by_text('Файл не подходит: данные не изменены. Выбери резервную копию IMlearning.',exact=True).wait_for()
    assert page.evaluate('MLStore.get().notes')==before['notes']
    # Simulate quota/security denial. UI must never claim a note was saved.
    page.evaluate("()=>{Storage.prototype.setItem=function(){throw new DOMException('Quota','QuotaExceededError')}}")
    page.goto(url+'/#lesson/09')
    page.locator('#lesson-note').fill('not persisted')
    assert 'Хранилище недоступно' in page.locator('#note-status').inner_text()
    # A fresh context has independent records, even on the same device.
    other=browser.new_context();second=other.new_page();second.goto(url+'/#course')
    second.locator('.module-card').first.wait_for()
    assert second.evaluate('MLStore.get().completed')==[]
    assert not errors,errors
    other.close();context.close();browser.close()
print('PASS migration, notes/answers/progress/labs, export/import, invalid backup and quota handling')
