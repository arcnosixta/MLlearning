"""Exercise real page transitions and actual media playback, not just UI labels."""
import os
import sys
import wave
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
with wave.open(str(ROOT / 'dist/audio/orbit.wav')) as music:
    assert music.getsampwidth() == 2 and music.getnchannels() == 1
    assert abs(music.getnframes() / music.getframerate() - 38.4) < .01
    assert any(music.readframes(22050))

with sync_playwright() as p:
    browser = p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    errors = []
    for lang in ['ru', 'kk']:
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        requests = []
        page.on('request', lambda r: requests.append(r.url) if '/audio/' in r.url else None)
        page.goto(URL + '/?lang=' + lang)
        page.locator('.studio-sound-toggle').wait_for()
        assert not requests, requests
        assert page.locator('.studio-title-line').count() == 3
        assert page.evaluate("getComputedStyle(document.querySelector('.studio-title-line')).animationName") == 'im-title-in'
        assert page.evaluate("document.querySelector('#studio-audio').paused")
        page.locator('.studio-sound-toggle').click()
        page.wait_for_function("document.querySelector('#studio-audio').currentTime > .15")
        expect(page.locator('.studio-sound-toggle')).to_have_attribute('aria-pressed', 'true')
        page.locator('.studio-sound-settings').click()
        page.locator('#studio-volume').fill('15')
        assert page.evaluate("document.querySelector('#studio-audio').volume") == .15
        page.keyboard.press('Escape')
        expect(page.locator('.studio-sound-panel')).to_be_hidden()
        page.evaluate("""() => {
          window.motionCalls = 0; window.transitionAnimation = '';
          const original = document.startViewTransition.bind(document);
          document.startViewTransition = (...args) => {
            window.motionCalls++;
            const t = original(...args);
            t.ready.then(() => window.transitionAnimation = getComputedStyle(document.documentElement, '::view-transition-new(studio-content)').animationName).catch(() => {});
            return t;
          };
        }""")
        before = page.evaluate("document.querySelector('#studio-audio').currentTime")
        page.locator('header nav a[href="#prepare"]').click()
        page.wait_for_function("window.transitionAnimation.includes('im-page-in')")
        page.locator('.studio-prepare').wait_for()
        assert page.evaluate('window.motionCalls') == 1
        assert page.evaluate("document.querySelector('#studio-audio').currentTime") >= before
        assert not page.evaluate("document.querySelector('#studio-audio').paused")
        # A rapid second navigation must leave the latest destination usable.
        page.locator('header nav a[href="#progress"]').click()
        page.locator('header nav a[href="#catalog"]').click()
        page.locator('.library-card').first.wait_for()
        page.reload()
        page.locator('.studio-sound-toggle').wait_for()
        assert page.evaluate("document.querySelector('#studio-audio').paused")
        page.locator('.studio-sound-settings').click()
        expect(page.locator('#studio-volume')).to_have_value('15')
        page.locator('[data-sound-play]').click()
        page.wait_for_function("!document.querySelector('#studio-audio').paused")
        page.locator('.studio-sound-toggle').click()
        expect(page.locator('.studio-sound-toggle')).to_have_attribute('aria-pressed', 'false')
        for width in [320, 390, 768, 1440]:
            page.set_viewport_size({'width': width, 'height': 900})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
            if width <= 390:
                assert abs(page.locator('header .brand').bounding_box()['y'] - page.locator('.language-switch').bounding_box()['y']) < 16
        # Stored preferences and playing state are cleared by the data action.
        page.goto(URL + '/?lang=' + lang + '#data')
        page.locator('#clear-data').wait_for()
        page.on('dialog', lambda d: d.accept())
        page.locator('#clear-data').click()
        assert page.evaluate("localStorage.getItem('imlearning-sound-v1')") is None
        assert page.evaluate("document.querySelector('#studio-audio').paused")
        page.close()

    # Fallback animation path works without the View Transition API.
    fallback = browser.new_page(reduced_motion='no-preference')
    fallback.add_init_script('document.startViewTransition = undefined')
    fallback.goto(URL + '/?lang=ru')
    fallback.locator('.studio-sound-toggle').wait_for()
    fallback.locator('header nav a[href="#progress"]').click()
    fallback.locator('.studio-dashboard').wait_for()
    expect(fallback.locator('body')).to_have_attribute('data-studio-page', 'study')
    fallback.close()
    # Accessibility preference bypasses the transition system entirely.
    reduced = browser.new_page(reduced_motion='reduce')
    reduced.add_init_script("document.startViewTransition = () => { throw new Error('Motion must be disabled'); }")
    reduced.on('pageerror', lambda e: errors.append(str(e)))
    reduced.goto(URL + '/?lang=kk')
    reduced.locator('.studio-sound-toggle').wait_for()
    assert reduced.evaluate("getComputedStyle(document.querySelector('.studio-title-line')).animationName") == 'none'
    reduced.locator('header nav a[href="#progress"]').click()
    reduced.locator('.studio-dashboard').wait_for()
    reduced.close()
    broken = browser.new_page()
    broken.on('pageerror', lambda e: errors.append(str(e)))
    broken.route('**/audio/orbit.wav', lambda r: r.abort())
    broken.goto(URL + '/?lang=ru')
    broken.locator('.studio-sound-toggle').click()
    broken.locator('.studio-sound-settings').click()
    expect(broken.locator('.studio-sound-panel [role="status"]')).to_contain_text('Попробуй')
    expect(broken.locator('.studio-sound-toggle')).to_have_attribute('aria-pressed', 'false')
    assert not errors, errors
    browser.close()
print('PASS actual audio playback/persistence/error handling, native/fallback transitions, rapid navigation and reduced motion')
