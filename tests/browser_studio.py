"""Validate redesigned learning flows, real progress and accessible motion."""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
OUT = Path(__file__).resolve().parents[1] / 'artifacts'
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())
    for lang in ['ru', 'kk']:
        def visit(route=''):
            page.goto(URL + '/?lang=' + lang + route)
            page.locator('header nav a[href="#progress"]').wait_for()

        visit()
        assert page.locator('.library-card').count() == 6
        page.locator('#studio-hours').fill('5')
        for step in range(3):
            page.locator('#studio-step').click()
            expect(page.locator('[data-code-step].is-active')).to_have_attribute('data-code-step', str(step))
        expect(page.locator('#studio-result')).to_have_text('300')
        expect(page.locator('#studio-step')).to_be_disabled()
        page.locator('#studio-reset').click()
        expect(page.locator('#studio-result')).to_have_text('—')
        page.locator('#studio-choose').click()
        expect(page).to_have_url(URL + '/?lang=' + lang + '#catalog')
        page.locator('#library-search').fill('Go')
        expect(page.locator('.library-card')).to_have_count(1)
        expect(page.locator('.teaching-card-link')).to_have_count(1)
        page.locator('#library-search').fill('')
        expect(page.locator('.library-card')).to_have_count(6)
        visit('#java')
        expect(page.locator('.studio-knowledge-node')).to_have_count(14)
        expect(page.locator('.studio-checkpoint')).to_have_count(2)
        page.locator('[data-studio-view="list"]').click()
        expect(page.locator('.week-grid')).to_have_class('week-grid studio-route-grid studio-list-view')
        page.locator('[data-java-phase="first"]').click()
        expect(page.locator('.studio-knowledge')).to_have_count(1)
        expect(page.locator('.studio-knowledge-node')).to_have_count(7)
        page.locator('[data-studio-view="list"]').click()
        visit('#track/go/01')
        expect(page.locator('.studio-reading-tools')).to_have_count(1)
        page.locator('#track-complete').click()
        visit('#track/go')
        expect(page.locator('.studio-knowledge-node.is-done')).to_have_count(1)
        visit('#progress')
        expect(page.locator('.studio-progress-list article')).to_have_count(7)
        expect(page.locator('[role="progressbar"][aria-label="Go"]')).to_have_attribute('aria-valuenow', '1')
        visit()
        expect(page.locator('.studio-hero a[href="#track/go/01"]')).to_have_count(1)
        visit('#learn/java/start')
        assert page.locator('.studio-reading-tools nav a').count() > 3
        page.locator('.studio-reading-tools>.button').click()
        expect(page.locator('#teaching-answer-0')).to_be_focused()
        visit('#prepare')
        expect(page.locator('.studio-control-links>a')).to_have_count(15)
        page.locator('.studio-control-links a[href="#exam/rk1"]').click()
        page.locator('#exam-start').click()
        page.locator('#exam-submit').click()
        page.locator('.exam-review').first.wait_for()
        visit('#prepare')
        page.locator('.studio-control-group details').first.locator('summary').click()
        result = page.locator('.studio-control-group details a').first
        expect(result).to_have_attribute('href', __import__('re').compile(r'#exam/result/.+'))
        result.click()
        page.locator('.exam-review').first.wait_for()

    # Reduced motion must show content immediately and suppress entrance effects.
    page.emulate_media(reduced_motion='reduce')
    visit()
    assert page.locator('.studio-reveal').count() == 0
    assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == 'auto'
    page.emulate_media(reduced_motion='no-preference')
    # Both reading and navigation remain usable at narrow and wide widths.
    for width in [320, 390, 768, 1440, 1920]:
        page.set_viewport_size({'width': width, 'height': 900})
        for route in ['', '#java', '#track/sysadmin', '#learn/java/start', '#lesson/01', '#progress', '#prepare', '#files/01']:
            visit(route)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, route)
            if width in [390, 1440] and route in ['', '#learn/java/start']:
                if not route:
                    page.locator('#studio-step').click()
                    page.locator('#studio-step').click()
                    page.locator('#studio-step').click()
                page.screenshot(path=str(OUT / f'studio-{width}-{"home" if not route else "lesson"}.png'))
    # Full local deletion clears the continuation pointer too.
    visit('#data')
    page.locator('#clear-data').click()
    assert page.evaluate("localStorage.getItem('imlearning-last-route')") is None
    assert not errors, errors
    browser.close()
print('PASS studio: bilingual demo, course map, real progress, resume, exam history, motion and responsive reading')
