"""Exercise ML persistence, legacy backup migration and denied writes."""
import json
import os
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

from browser_ready import goto_ready

url = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
with sync_playwright() as p, tempfile.TemporaryDirectory() as temporary:
    browser = p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    context = browser.new_context(accept_downloads=True, reduced_motion='reduce')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: dialog.accept())
    goto_ready(page, url + '/?lang=ru#course')
    page.evaluate("localStorage.clear(); localStorage.setItem('mllearning-progress','[\"01\"]')")
    page.reload()
    page.locator('.ml-weeks').wait_for()
    assert page.evaluate('MLStore.get().completed') == ['01']
    assert page.evaluate('MLStore.get().mlSemester.completed') == []
    goto_ready(page, url + '/#course/week/09')
    page.locator('#ml-note').fill('Менің жазбам <script>alert(1)</script> — личная заметка')
    page.locator('#ml-result-1').fill('Результат первого опыта')
    answer = page.locator('.ml-quiz').first.locator('[data-answer="0"]')
    answer.click()
    page.locator('#ml-complete').click()
    page.reload()
    page.locator('#ml-note').wait_for()
    assert 'Менің жазбам' in page.locator('#ml-note').input_value()
    assert page.locator('#ml-result-1').input_value() == 'Результат первого опыта'
    assert answer.get_attribute('aria-pressed') == 'true'
    assert page.locator('#ml-complete').get_attribute('aria-pressed') == 'true'
    page.locator('#ml-complete').click()
    assert page.evaluate('MLStore.get().mlSemester.completed') == []
    page.locator('#ml-complete').click()
    goto_ready(page, url + '/#progress')
    assert page.locator('a[href="#course/week/09"]').count()
    goto_ready(page, url + '/#data')
    before = page.evaluate('MLStore.get()')
    with page.expect_download() as pending:
        page.locator('#export-data').click()
    backup = Path(temporary) / 'backup.json'
    pending.value.save_as(backup)
    exported = json.loads(backup.read_text(encoding='utf-8'))
    assert exported['completed'] == ['01'] and exported['mlSemester']['completed'] == ['09']
    page.locator('#clear-data').click()
    assert page.evaluate('MLStore.get().mlSemester.notes') == {}
    page.locator('#import-data').set_input_files(backup)
    page.get_by_text('Данные восстановлены', exact=True).wait_for()
    assert page.evaluate('MLStore.get().mlSemester') == before['mlSemester']
    invalid = Path(temporary) / 'invalid.json'
    exported['mlSemester']['answers']['99/1'] = 0
    invalid.write_text(json.dumps(exported), encoding='utf-8')
    page.locator('#import-data').set_input_files(invalid)
    page.get_by_text('Файл не подходит: данные не изменены. Выбери резервную копию IMlearning.', exact=True).wait_for()
    assert page.evaluate('MLStore.get().mlSemester') == before['mlSemester']
    page.evaluate("()=>{Storage.prototype.setItem=function(){throw new DOMException('Quota','QuotaExceededError')}}")
    goto_ready(page, url + '/#course/week/09')
    page.locator('#ml-note').fill('not persisted')
    assert 'до закрытия страницы' in page.locator('.ml-assignment .ml-save').inner_text()
    other = browser.new_page()
    goto_ready(other, url + '/#course')
    assert other.evaluate('MLStore.get().mlSemester.completed') == []
    assert not errors, errors
    browser.close()
print('PASS ML migration, notes, quiz answers, lab reports, progress, backup and quota handling')
