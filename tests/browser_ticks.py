"""Verify synthesized hover ticks, nested targets, opt-out and old preferences."""
import os
import sys
from playwright.sync_api import sync_playwright, expect
from browser_ready import goto_ready

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
with sync_playwright() as p:
    browser = p.chromium.launch(channel=os.environ.get('PLAYWRIGHT_CHANNEL') or None)
    for lang in ['ru', 'kk']:
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.add_init_script("""(() => {
          const Native = window.AudioContext;
          window.tickCount = 0;
          window.AudioContext = class extends Native {
            constructor(...args) { super(...args); window.tickContext = this; }
            createBufferSource() {
              const source = super.createBufferSource(), start = source.start.bind(source);
              source.start = (...args) => {
                window.tickCount++;
                window.tickDuration = source.buffer.duration;
                window.tickHasSignal = source.buffer.getChannelData(0).some(x => Math.abs(x) > .05);
                return start(...args);
              };
              return source;
            }
          };
        })()""")
        goto_ready(page, URL + '/?lang=' + lang)
        assert page.evaluate('window.tickCount') == 0
        page.locator('h1').click()
        page.wait_for_function("window.tickContext?.state === 'running'")

        def hover(selector):
            page.locator(selector).first.hover()
            page.wait_for_timeout(100)
            return page.evaluate('window.tickCount')

        count = hover('.studio-sound-toggle')
        assert count >= 1
        assert hover('.studio-equalizer i') == count  # Still within the same button.
        assert page.evaluate('window.tickHasSignal')
        assert .02 < page.evaluate('window.tickDuration') < .04
        assert page.evaluate("document.querySelector('#studio-audio').paused")
        count = hover('.library-card h3')
        assert hover('.library-card .course-symbol') == count
        assert hover('.library-card .button') == count + 1
        count = page.evaluate('window.tickCount')
        assert hover('.library-card h3') == count  # Returning from a child button.
        page.locator('.library-card').first.dispatch_event('pointerover', {'pointerType': 'touch'})
        assert page.evaluate('window.tickCount') == count
        page.evaluate("""() => {
          const button = document.querySelector('.studio-sound-settings');
          button.disabled = true;
          button.dispatchEvent(new PointerEvent('pointerover', {bubbles:true,pointerType:'mouse'}));
          button.disabled = false;
        }""")
        assert page.evaluate('window.tickCount') == count
        # Rapid enter events cannot create a burst of overlapping ticks.
        page.evaluate("""() => {
          const button = document.querySelector('.studio-sound-settings');
          for (let i = 0; i < 20; i++) button.dispatchEvent(new PointerEvent('pointerover', {bubbles:true,pointerType:'mouse'}));
        }""")
        assert page.evaluate('window.tickCount') <= count + 1
        page.locator('.studio-sound-settings').click()
        page.locator('#studio-tick-volume').fill('18')
        page.locator('#studio-ticks').uncheck()
        page.keyboard.press('Escape')
        count = hover('.studio-sound-toggle')
        assert hover('.library-card h3') == count
        page.reload()
        page.locator('.studio-sound-settings').click()
        expect(page.locator('#studio-ticks')).not_to_be_checked()
        expect(page.locator('#studio-tick-volume')).to_have_value('18')
        page.locator('#studio-ticks').check()
        page.wait_for_function("window.tickContext?.state === 'running'")
        page.locator('#studio-tick-volume').fill('0')
        page.keyboard.press('Escape')
        count = hover('.studio-sound-toggle')
        assert hover('.library-card h3') == count
        goto_ready(page, URL + '/?lang=' + lang + '#data')
        page.on('dialog', lambda d: d.accept())
        page.locator('#clear-data').click()
        assert page.evaluate("localStorage.getItem('imlearning-sound-v1')") is None
        page.locator('.studio-sound-settings').click()
        expect(page.locator('#studio-ticks')).to_be_checked()
        expect(page.locator('#studio-tick-volume')).to_have_value('35')
        assert not errors, errors
        page.close()

    # Existing music-only settings migrate without changing volume or enabling music.
    old = browser.new_page()
    old.add_init_script("localStorage.setItem('imlearning-sound-v1', JSON.stringify({enabled:false,volume:.12}))")
    goto_ready(old, URL + '/?lang=ru')
    old.locator('.studio-sound-settings').click()
    expect(old.locator('#studio-ticks')).to_be_checked()
    expect(old.locator('#studio-volume')).to_have_value('12')
    browser.close()
print('PASS real short hover audio, nested target deduplication, throttling, touch, saved controls, reset and migration')
