/* Browser-owned playback; enabling the saved preference never bypasses a gesture. */
const studioSound = (() => {
  const key = 'imlearning-sound-v1';
  let preferences = {enabled: false, volume: .25};
  try {
    const saved = JSON.parse(localStorage.getItem(key));
    if (saved && typeof saved.enabled === 'boolean' && Number.isFinite(saved.volume)) {
      preferences = {enabled: saved.enabled, volume: Math.max(0, Math.min(1, saved.volume))};
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
  const persist = () => {
    try { localStorage.setItem(key, JSON.stringify(preferences)); } catch {}
  };
  function update() {
    if (!button) return;
    const playing = !audio.paused;
    button.classList.toggle('is-playing', playing);
    button.setAttribute('aria-pressed', String(playing));
    button.setAttribute('aria-label', playing ? jt('Выключить музыку', 'Музыканы өшіру') : jt('Включить музыку', 'Музыканы қосу'));
    button.querySelector('.studio-sound-label').textContent = playing ? jt('Звук: вкл', 'Дыбыс: қосулы') : jt('Звук: выкл', 'Дыбыс: өшірулі');
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
  return {init, reset() { audio.pause(); audio.currentTime = 0; preferences = {enabled: false, volume: .25}; audio.volume = .25; error = ''; try { localStorage.removeItem(key); } catch {} if (panel) { panel.querySelector('#studio-volume').value = '25'; panel.querySelector('#studio-volume-value').textContent = '25%'; } update(); }};
})();
