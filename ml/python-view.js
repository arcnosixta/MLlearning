let mlPythonDispose;

function mlPythonHTML(id, assets) {
  const dataset = assets.includes('data.csv');
  const experiments = assets.includes('experiments.py');
  return `<details class="ml-code ml-python" data-source="ml/${id}/lab.py" ${dataset ? `data-dataset="ml/${id}/data.csv"` : ''}>
    <summary>${jt('Открыть редактор Python', 'Python редакторын ашу')}</summary>
    <p>${jt('Измени пример и запусти его в браузере. При первом запуске загрузятся Python и нужные библиотеки.', 'Мысалды өзгертіп, браузерде іске қос. Алғашқы іске қосқанда Python мен қажетті кітапханалар жүктеледі.')}</p>
    ${dataset ? `<p class="ml-python-dataset"><code>data.csv</code> · ${jt('данные этой лабораторной доступны из кода', 'осы зертхана деректері кодтан қолжетімді')}</p>` : ''}
    ${experiments ? `<label for="ml-python-source">${jt('Пример для запуска', 'Іске қосатын мысал')}</label>
    <select id="ml-python-source">
      <option value="ml/${id}/lab.py">${jt('Короткий пример — lab.py', 'Қысқа мысал — lab.py')}</option>
      <option value="ml/${id}/experiments.py">${jt('Все опыты урока — experiments.py', 'Сабақтың барлық тәжірибесі — experiments.py')}</option>
    </select><p>${jt('Начни с короткого примера: измени одно значение, запусти и сравни результат. Все подробные опыты доступны во втором варианте.', 'Қысқа мысалдан баста: бір мәнді өзгерт, іске қосып, нәтижені салыстыр. Барлық толық тәжірибе екінші нұсқада бар.')}</p>` : ''}
    <label for="ml-python-editor" id="ml-python-filename">lab.py</label>
    <textarea id="ml-python-editor" rows="16" maxlength="100000" spellcheck="false" autocapitalize="off" autocomplete="off" disabled></textarea>
    <div class="ml-python-actions">
      <button type="button" id="ml-python-run" class="button" aria-keyshortcuts="Control+Enter Meta+Enter" disabled>${jt('Запустить Python', 'Python іске қосу')} ▶</button>
      <button type="button" id="ml-python-stop" class="button outline" disabled>${jt('Остановить', 'Тоқтату')}</button>
      <button type="button" id="ml-python-reset" class="button outline" disabled>${jt('Восстановить пример', 'Мысалды қалпына келтіру')}</button>
    </div>
    <p id="ml-python-status" role="status" data-state="loading"></p>
    <details class="ml-python-console" open>
      <summary>${jt('Вывод Python', 'Python нәтижесі')}</summary>
      <pre id="ml-python-output" tabindex="0" aria-label="${jt('Консоль Python', 'Python консолі')}"></pre>
    </details>
    <div class="ml-python-figures"></div>
    <details id="ml-python-experiment" hidden>
      <summary>${jt('График по результатам запуска', 'Іске қосу нәтижесінің графигі')}</summary>
      <div class="ml-python-selects">
        <label for="ml-python-topic">${jt('Тема', 'Тақырып')} <select id="ml-python-topic"></select></label>
        <label for="ml-python-case">${jt('Условие опыта', 'Тәжірибе шарты')} <select id="ml-python-case"></select></label>
      </div>
      <figure><div class="ml-chart-output"></div><figcaption></figcaption></figure>
    </details>
  </details>`;
}

async function mlPythonFile(path, signal) {
  const response = await fetch(path, {signal: AbortSignal.any([signal, AbortSignal.timeout(15000)])});
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.text();
}

function mlBindPython(details, lesson, week) {
  const find = selector => details.querySelector(selector);
  const editor = find('#ml-python-editor'), run = find('#ml-python-run');
  const stop = find('#ml-python-stop'), reset = find('#ml-python-reset');
  const status = find('#ml-python-status'), console = find('#ml-python-output');
  const figures = find('.ml-python-figures'), experiment = find('#ml-python-experiment');
  const sourceSelect = find('#ml-python-source'), filename = find('#ml-python-filename');
  const sources = new Map(), drafts = new Map();
  let currentSource = details.dataset.source;
  const lifetime = new AbortController();
  const setExperiment = mlBindPythonPlot(experiment, lesson, week, lifetime.signal);
  const messages = {
    ready: jt('Редактор готов.', 'Редактор дайын.'),
    loading: jt('Загружаем Python и файлы урока…', 'Python мен сабақ файлдары жүктелуде…'),
    packages: jt('Подключаем библиотеки…', 'Кітапханалар қосылуда…'),
    running: jt('Выполняем код…', 'Код орындалуда…'),
    success: jt('Код выполнен.', 'Код орындалды.'),
    error: jt('Запуск завершился с ошибкой.', 'Орындау қатемен аяқталды.'),
    stopped: jt('Выполнение остановлено.', 'Орындау тоқтатылды.'),
  };
  let source, sourceLoading, dataset, worker, active, nextId = 0, outputSize = 0;

  function setState(state, message = messages[state]) {
    status.dataset.state = state;
    status.textContent = message;
    run.disabled = source === undefined || Boolean(active) || !editor.value.trim();
    reset.disabled = Boolean(active) || Boolean(sourceLoading);
    stop.disabled = !active;
    editor.disabled = source === undefined || Boolean(active);
    if (sourceSelect) sourceSelect.disabled = Boolean(active) || Boolean(sourceLoading);
  }

  function appendOutput(text, stream = 'stdout') {
    const limit = 120000;
    if (typeof text !== 'string' || outputSize >= limit) return;
    const chunk = document.createElement('span');
    chunk.className = stream === 'stderr' ? 'ml-python-stderr' : 'ml-python-stdout';
    chunk.textContent = text.slice(0, limit - outputSize);
    outputSize += chunk.textContent.length;
    console.append(chunk);
    if (outputSize === limit) console.append(`\n${jt('Вывод сокращён.', 'Нәтиже қысқартылды.')}\n`);
  }

  function finish(state, message, terminate = false) {
    active?.controller.abort();
    clearTimeout(active?.timer);
    active = undefined;
    if (terminate) {
      worker?.terminate();
      worker = undefined;
    }
    setState(state, message);
  }

  function setTimeoutForRun(milliseconds, message) {
    clearTimeout(active.timer);
    active.timer = setTimeout(() => finish('error', message, true), milliseconds);
  }

  function handleWorker(message) {
    if (!active || message?.id !== active.id) return;
    if (message.type === 'status' && ['loading', 'packages', 'running'].includes(message.phase)) {
      setState(message.phase);
      if (message.phase === 'running') setTimeoutForRun(45000, jt('Превышен лимит выполнения в 45 секунд.', '45 секундтық орындау шегі асырылды.'));
    } else if (message.type === 'output') {
      appendOutput(message.text, message.stream);
    } else if (message.type === 'error') {
      appendOutput(`\n${String(message.message ?? '')}\n`, 'stderr');
      // A failed runtime or package download may be cached inside this worker.
      finish('error', undefined, status.dataset.state !== 'running');
    } else if (message.type === 'result') {
      const images = Array.isArray(message.figures) ? message.figures.slice(0, 6) : [];
      for (const [index, data] of images.entries()) {
        if (typeof data !== 'string' || data.length > 1500000 || !/^iVBORw0KGgo[A-Za-z0-9+/=]+$/.test(data)) continue;
        const image = document.createElement('img');
        image.src = `data:image/png;base64,${data}`;
        image.alt = `${jt('График Python', 'Python графигі')} ${index + 1}`;
        const frame = document.createElement('figure'), viewport = document.createElement('div');
        const zoom = document.createElement('button');
        viewport.className = 'ml-python-image';
        viewport.tabIndex = 0;
        viewport.setAttribute('aria-label', image.alt);
        viewport.append(image);
        zoom.type = 'button';
        zoom.className = 'button outline ml-python-zoom';
        zoom.textContent = jt('Увеличить график', 'Графикті үлкейту');
        zoom.setAttribute('aria-pressed', 'false');
        zoom.onclick = () => {
          const enlarged = viewport.classList.toggle('is-enlarged');
          zoom.setAttribute('aria-pressed', String(enlarged));
          zoom.textContent = enlarged ? jt('Вписать в экран', 'Экранға сыйғызу') : jt('Увеличить график', 'Графикті үлкейту');
        };
        frame.append(viewport, zoom);
        figures.append(frame);
      }
      setExperiment(message.experiment);
      if (message.experiment) appendOutput(jt(
        `Построены графики: ${message.experiment.topics.length} темы. Выбери тему и условие опыта ниже.\n`,
        `Графиктер құрылды: ${message.experiment.topics.length} тақырып. Төменде тақырып пен тәжірибе шартын таңда.\n`,
      ));
      finish('success');
    }
  }

  async function loadSource() {
    if (source !== undefined || sourceLoading) return;
    sourceLoading = true;
    setState('loading', jt('Загружаем пример…', 'Мысал жүктелуде…'));
    let failure;
    try {
      source = sources.get(currentSource) ?? await mlPythonFile(currentSource, lifetime.signal);
      sources.set(currentSource, source);
      editor.value = drafts.get(currentSource) ?? source;
      filename.textContent = currentSource.split('/').pop();
    } catch {
      failure = jt('Не удалось загрузить пример. Нажми «Восстановить пример», чтобы повторить.', 'Мысал жүктелмеді. Қайталау үшін «Мысалды қалпына келтіру» батырмасын бас.');
    } finally {
      sourceLoading = false;
      if (!lifetime.signal.aborted) setState(failure ? 'error' : 'ready', failure);
    }
  }

  async function execute() {
    if (active || source === undefined || !editor.value.trim()) return;
    const job = {id: ++nextId, controller: new AbortController()};
    active = job;
    console.replaceChildren();
    figures.replaceChildren();
    setExperiment();
    outputSize = 0;
    find('.ml-python-console').open = true;
    setState('loading');
    setTimeoutForRun(120000, jt('Загрузка Python или библиотек заняла слишком много времени. Попробуй ещё раз.', 'Python не кітапханалар тым ұзақ жүктелді. Қайта байқап көр.'));
    try {
      if (details.dataset.dataset && dataset === undefined) {
        dataset = await mlPythonFile(details.dataset.dataset, job.controller.signal);
      }
      if (active !== job) return;
      if (!worker) {
        const instance = new Worker('ml/python-worker.js', {type: 'module'});
        instance.onmessage = event => { if (worker === instance) handleWorker(event.data); };
        instance.onerror = event => {
          if (worker !== instance || !active) return;
          event.preventDefault();
          finish('error', jt('Среда Python не загрузилась. Проверь соединение и повтори запуск.', 'Python ортасы жүктелмеді. Байланысты тексеріп, қайта іске қос.'), true);
        };
        worker = instance;
      }
      worker.postMessage({type: 'run', id: job.id, code: editor.value,
        language: window.ML_LOCALE === 'kk' ? 'kk' : 'ru', topicCount: week.topics.length,
        ...(dataset === undefined ? {} : {dataset: {name: 'data.csv', text: dataset}})});
    } catch {
      if (active === job) finish('error', jt('Не удалось начать запуск. Проверь соединение и попробуй ещё раз.', 'Орындау басталмады. Байланысты тексеріп, қайта байқап көр.'), true);
    }
  }

  details.addEventListener('toggle', () => { if (details.open) loadSource(); });
  if (sourceSelect) sourceSelect.onchange = () => {
    drafts.set(currentSource, editor.value);
    currentSource = sourceSelect.value;
    source = undefined;
    console.replaceChildren();
    figures.replaceChildren();
    setExperiment();
    loadSource();
  };
  reset.onclick = () => {
    if (source === undefined) loadSource();
    else {
      editor.value = source;
      drafts.delete(currentSource);
      console.replaceChildren();
      figures.replaceChildren();
      setExperiment();
      setState('ready');
      editor.focus();
    }
  };
  run.onclick = execute;
  stop.onclick = () => { if (active) finish('stopped', undefined, true); };
  editor.addEventListener('input', () => { run.disabled = Boolean(active) || !editor.value.trim(); });
  editor.addEventListener('keydown', event => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      execute();
    }
  });
  return () => {
    lifetime.abort();
    active?.controller.abort();
    clearTimeout(active?.timer);
    active = undefined;
    worker?.terminate();
    worker = undefined;
  };
}

function mlPythonChartTopics(data, count) {
  if (!Array.isArray(data?.topics) || data.topics.length !== count || count < 1 || count > 6) return;
  const bilingual = label => ['ru', 'kk'].every(lang => typeof label?.[lang] === 'string' && label[lang].length > 0 && label[lang].length <= 1200);
  const number = value => Number.isFinite(value) && Math.abs(value) <= 1e100;
  const seriesValid = series => bilingual(series?.label) && ['line', 'bar', 'scatter'].includes(series.kind) &&
    Array.isArray(series.points) && series.points.length > 0 && series.points.length <= 1000 &&
    series.points.every(point => Array.isArray(point) && point.length === 2 && point.every(number));
  const caseValid = item => bilingual(item?.label) && bilingual(item.note) && Array.isArray(item.series) &&
    item.series.length > 0 && item.series.length <= 16 && item.series.every(seriesValid) &&
    (item.xTicks === undefined || (Array.isArray(item.xTicks) && item.xTicks.length <= 32 &&
      item.xTicks.every(tick => number(tick?.value) && bilingual(tick.label))));
  if (data.topics.every(cases => Array.isArray(cases) && cases.length > 0 && cases.length <= 6 && cases.every(caseValid))) return data.topics;
}

function mlBindPythonPlot(details, lesson, week, signal) {
  const topic = details.querySelector('#ml-python-topic'), select = details.querySelector('#ml-python-case');
  const output = details.querySelector('.ml-chart-output'), caption = details.querySelector('figcaption');
  const options = labels => labels.map((label, i) => new Option(label, String(i)));
  topic.replaceChildren(...options(week.topics.map(item => item.title)));
  let topics, previousWidth;

  function width() { return Math.max(195, Math.min(590, output.clientWidth - 10)); }

  function draw() {
    if (!topics || !details.open) return;
    const index = Number(topic.value), cases = topics[index], current = cases[Number(select.value)];
    previousWidth = width();
    output.innerHTML = mlPlot(cases, current, week.topics[index], lesson.independentAxes?.includes(index + 1), previousWidth);
    caption.textContent = mlText(current.note);
  }

  function showCases() {
    select.replaceChildren(...options(topics[Number(topic.value)].map(item => mlText(item.label))));
    draw();
  }

  topic.addEventListener('change', showCases);
  select.addEventListener('change', draw);
  details.addEventListener('toggle', draw);
  const observer = new ResizeObserver(() => { if (previousWidth !== width()) draw(); });
  observer.observe(output);
  signal.addEventListener('abort', () => observer.disconnect(), {once: true});
  return data => {
    topics = mlPythonChartTopics(data, week.topics.length);
    details.hidden = !topics;
    details.open = Boolean(topics);
    if (topics) {
      topic.value = '0';
      showCases();
    } else {
      output.replaceChildren();
      caption.textContent = '';
    }
  };
}
