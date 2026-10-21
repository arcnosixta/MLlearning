/* Browser-owned playback; enabling the saved preference never bypasses a gesture. */
const studioSound = (() => {
  const key = 'imlearning-sound-v1';
  let preferences = {enabled: false, volume: .25, ticks: true, tickVolume: .35};
  try {
    const saved = JSON.parse(localStorage.getItem(key));
    if (saved && typeof saved.enabled === 'boolean' && Number.isFinite(saved.volume)) {
      preferences = {
        enabled: saved.enabled, volume: Math.max(0, Math.min(1, saved.volume)),
        ticks: typeof saved.ticks === 'boolean' ? saved.ticks : true,
        tickVolume: Number.isFinite(saved.tickVolume) ? Math.max(0, Math.min(1, saved.tickVolume)) : .35
      };
    }
  } catch {}
  const audio = new Audio('audio/orbit.wav');
  audio.id = 'studio-audio';
  audio.hidden = true;
  audio.loop = true;
  audio.preload = 'none';
  audio.volume = preferences.volume;
  let error = '';
  let button, panel;
  let tickContext, tickBuffer, lastTick = -Infinity;
  // Browsers unlock audio on a click/key press; hovering alone cannot unlock it.
  function armTicks() {
    if (!preferences.ticks) return;
    try {
      const Context = window.AudioContext || window.webkitAudioContext;
      if (!Context) return;
      if (!tickContext) {
        tickContext = new Context();
        tickBuffer = tickContext.createBuffer(1, Math.ceil(tickContext.sampleRate * .026), tickContext.sampleRate);
        const samples = tickBuffer.getChannelData(0);
        let seed = 7123;
        for (let i = 0; i < samples.length; i++) {
          seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
          samples[i] = (seed / 4294967296 * 2 - 1) * Math.exp(-i / (tickContext.sampleRate * .004));
        }
      }
      if (tickContext.state === 'suspended') tickContext.resume().catch(() => {});
    } catch { /* Learning and background music remain available without Web Audio. */ }
  }
  function tick() {
    if (!preferences.ticks || !preferences.tickVolume || tickContext?.state !== 'running') return;
    const clock = performance.now();
    if (clock - lastTick < 70) return;
    lastTick = clock;
    const source = tickContext.createBufferSource();
    const filter = tickContext.createBiquadFilter();
    const gain = tickContext.createGain();
    source.buffer = tickBuffer;
    filter.type = 'bandpass'; filter.frequency.value = 2100; filter.Q.value = .8;
    gain.gain.value = preferences.tickVolume * .7;
    source.connect(filter).connect(gain).connect(tickContext.destination);
    source.onended = () => { source.disconnect(); filter.disconnect(); gain.disconnect(); };
    source.start();
  }
  function hoverTick(event) {
    if (event.pointerType !== 'mouse' || !(event.target instanceof Element)) return;
    const target = event.target.closest('button,a[href],summary,[role="button"],.library-card,.module-card,.week-card,.track-module,.file-card,.subject-card,.teaching-exercise,.studio-demo,.studio-progress-list>article');
    if (!target || target.contains(event.relatedTarget) || target.matches(':disabled,[aria-disabled="true"]') || target.closest('[inert]')) return;
    tick();
  }
  const persist = () => {
    try { localStorage.setItem(key, JSON.stringify(preferences)); } catch {}
  };
  function update() {
    if (!button) return;
    const playing = !audio.paused;
    button.classList.toggle('is-playing', playing);
    button.setAttribute('aria-pressed', String(playing));
    button.setAttribute('aria-label', playing ? jt('Выключить музыку', 'Музыканы өшіру') : jt('Включить музыку', 'Музыканы қосу'));
    button.querySelector('.studio-sound-label').textContent = playing ? jt('Музыка: вкл', 'Музыка: қосулы') : jt('Музыка: выкл', 'Музыка: өшірулі');
    if (panel) {
      panel.querySelector('[data-sound-play]').textContent = playing ? jt('Пауза', 'Үзіліс') : jt('Включить музыку', 'Музыканы қосу');
      panel.querySelector('[role="status"]').textContent = error || (playing ? jt('Играет Orbit · зациклено', 'Orbit ойнап тұр · қайталанады') : preferences.enabled ? jt('Нажми ▶, чтобы продолжить музыку.', 'Музыканы жалғастыру үшін ▶ бас.') : jt('Фоновая музыка выключена.', 'Фондық музыка өшірулі.'));
    }
  }
  async function toggle() {
    error = '';
    if (!audio.paused) {
      audio.pause();
      preferences.enabled = false;
    } else {
      try {
        if (audio.error) audio.load();
        await audio.play();
        preferences.enabled = true;
      } catch {
        preferences.enabled = false;
        error = jt('Не удалось загрузить музыку. Попробуй ещё раз.', 'Музыканы жүктеу мүмкін емес. Қайталап көр.');
      }
    }
    persist(); update();
  }
  function init() {
    if (button) { update(); return; }
    const controls = document.createElement('div');
    controls.className = 'studio-sound';
    controls.innerHTML = `<button class="studio-sound-toggle" type="button" aria-pressed="false"><span class="studio-equalizer" aria-hidden="true"><i></i><i></i><i></i><i></i></span><span class="studio-sound-label"></span></button><button class="studio-sound-settings" type="button" aria-expanded="false" aria-controls="studio-sound-panel" aria-label="${jt('Настройки музыки','Музыка баптаулары')}">⌄</button><div class="studio-sound-panel" id="studio-sound-panel" hidden><span class="eyebrow">IM / ${jt('МУЗЫКА ДЛЯ УЧЁБЫ','ОҚУҒА АРНАЛҒАН МУЗЫКА')}</span><strong>Orbit <span>01 / AMBIENT</span></strong><p>${jt('Спокойный инструментальный фон без слов.','Сөзсіз тыныш аспаптық әуен.')}</p><button class="button" data-sound-play type="button"></button><label for="studio-volume">${jt('Громкость','Дыбыс деңгейі')} <output id="studio-volume-value"></output></label><input id="studio-volume" type="range" min="0" max="100" value="${Math.round(preferences.volume * 100)}"><p role="status" aria-live="polite"></p></div>`;
    controls.append(audio);
    document.querySelector('header').insertBefore(controls, document.querySelector('.language-switch'));
    button = controls.querySelector('.studio-sound-toggle');
    panel = controls.querySelector('.studio-sound-panel');
    controls.querySelector('.studio-sound-settings').setAttribute('aria-label', jt('Настройки звука', 'Дыбыс баптаулары'));
    const ticks = document.createElement('section');
    ticks.className = 'studio-tick-settings';
    ticks.innerHTML = `<label class="studio-tick-switch" for="studio-ticks"><span>${jt('Тик при наведении','Меңзегендегі тықыл')}</span><input id="studio-ticks" type="checkbox" ${preferences.ticks ? 'checked' : ''}></label><label for="studio-tick-volume">${jt('Громкость тика','Тықыл дыбысының деңгейі')} <output id="studio-tick-volume-value">${Math.round(preferences.tickVolume * 100)}%</output></label><input id="studio-tick-volume" type="range" min="0" max="100" value="${Math.round(preferences.tickVolume * 100)}"><p>${jt('Звуки интерфейса работают отдельно от музыки. После первого клика наведи курсор на кнопку или карточку.','Интерфейс дыбыстары музыкадан бөлек жұмыс істейді. Алғашқы басудан кейін меңзерді батырмаға не карточкаға апар.')}</p>`;
    panel.append(ticks);
    ticks.querySelector('#studio-ticks').onchange = event => {
      preferences.ticks = event.target.checked; persist();
      if (preferences.ticks) { armTicks(); tick(); }
    };
    ticks.querySelector('#studio-tick-volume').oninput = event => {
      preferences.tickVolume = Number(event.target.value) / 100;
      ticks.querySelector('output').textContent = event.target.value + '%'; persist();
    };
    document.addEventListener('pointerdown', armTicks, {passive: true});
    document.addEventListener('keydown', armTicks);
    document.addEventListener('pointerover', hoverTick, {passive: true});
    button.onclick = toggle;
    panel.querySelector('[data-sound-play]').onclick = toggle;
    const settings = controls.querySelector('.studio-sound-settings');
    function close() { panel.hidden = true; settings.setAttribute('aria-expanded', 'false'); }
    settings.onclick = () => { panel.hidden = !panel.hidden; settings.setAttribute('aria-expanded', String(!panel.hidden)); };
    document.addEventListener('click', e => { if (!controls.contains(e.target)) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) { close(); settings.focus(); } });
    const volume = panel.querySelector('#studio-volume');
    const showVolume = () => { panel.querySelector('#studio-volume-value').textContent = volume.value + '%'; };
    volume.oninput = () => { preferences.volume = Number(volume.value) / 100; audio.volume = preferences.volume; showVolume(); persist(); };
    showVolume(); update();
  }
  audio.addEventListener('play', update);
  audio.addEventListener('pause', update);
  audio.addEventListener('error', () => { error = jt('Музыка недоступна. Попробуй ещё раз.', 'Музыка қолжетімсіз. Қайталап көр.'); update(); });
  return {init, reset() { audio.pause(); audio.currentTime = 0; preferences = {enabled: false, volume: .25, ticks: true, tickVolume: .35}; audio.volume = .25; error = ''; try { localStorage.removeItem(key); } catch {} if (panel) { panel.querySelector('#studio-volume').value = '25'; panel.querySelector('#studio-volume-value').textContent = '25%'; panel.querySelector('#studio-ticks').checked = true; panel.querySelector('#studio-tick-volume').value = '35'; panel.querySelector('#studio-tick-volume-value').textContent = '35%'; } update(); }};
})();
