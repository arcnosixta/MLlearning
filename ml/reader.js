let mlPlotObserver;

function mlTopicHTML(topic, cases, index) {
  const n = index + 1;
  return `<section class="ml-topic" id="ml-topic-${n}" tabindex="-1" aria-labelledby="ml-title-${n}">
    <div class="eyebrow">${jt('ТЕМА', 'ТАҚЫРЫП')} ${String(n).padStart(2, '0')}</div><h2 id="ml-title-${n}">${escapeHTML(topic.title)}</h2>
    ${topic.theory.map(text => `<p>${escapeHTML(text)}</p>`).join('')}
    <div class="ml-example"><h3>${jt('Разбор примера', 'Мысалды талдау')}</h3><p>${escapeHTML(topic.example)}</p></div>
    <div class="ml-lab" data-ml-topic="${n}">
      <h3>${jt('Лабораторная', 'Зертханалық жұмыс')} · ${escapeHTML(topic.title)}</h3>
      <p>${escapeHTML(topic.task)}</p>
      <label for="ml-case-${n}">${jt('Условие опыта', 'Тәжірибе шарты')}</label>
      <select id="ml-case-${n}" class="ml-case">${cases.map((item, i) => `<option value="${i}">${escapeHTML(mlText(item.label))}</option>`).join('')}</select>
      <figure><div class="ml-chart-output"></div><figcaption aria-live="polite"></figcaption></figure>
      <details class="ml-points"><summary>${jt('Данные графика', 'График деректері')}</summary><div class="ml-table"></div></details>
      <label for="ml-result-${n}">${jt('Запиши результат и вывод', 'Нәтиже мен қорытындыны жаз')}</label>
      <textarea id="ml-result-${n}" class="ml-result" maxlength="10000" rows="3"></textarea><small class="ml-save" role="status"></small>
      <details><summary>${jt('Подсказка', 'Кеңес')}</summary><p>${escapeHTML(topic.hint)}</p></details>
      <details><summary>${jt('Разбор результата', 'Нәтижені талдау')}</summary><p>${escapeHTML(topic.solution)}</p></details>
    </div>
    <fieldset class="ml-quiz" data-ml-quiz="${n}"><legend>${jt('Проверь себя', 'Өзіңді тексер')}</legend><p>${escapeHTML(topic.question)}</p>
    <div class="ml-answers">${topic.choices.map((choice, i) => `<button type="button" data-answer="${i}" aria-pressed="false">${escapeHTML(choice)}</button>`).join('')}</div><p class="ml-feedback" role="status"></p></fieldset>
  </section>`;
}

function mlWeekPage(lesson, data) {
  const {id} = lesson, week = mlText(lesson), project = id === 'project';
  if (!project) MLStore.mlUpdate({lastWeek: id});
  const record = MLStore.get().mlSemester;
  const number = Number(id), adjacent = step => mlWeekHref(String(number + step).padStart(2, '0'));
  main.innerHTML = `<article class="tracks-page ml-reader">
    <a class="breadcrumb" href="#course">← ${jt('Программа ML', 'ML бағдарламасы')}</a>
    <div class="ml-reader-head"><div class="eyebrow">ML 3305 / ${project ? jt('ИТОГОВЫЙ ПРАКТИКУМ', 'ҚОРЫТЫНДЫ ПРАКТИКУМ') : `${jt('НЕДЕЛЯ', 'АПТА')} ${id} / 14`}</div><h1>${escapeHTML(week.title)}</h1><p class="lesson-intro">${escapeHTML(week.intro)}</p></div>
    <div class="ml-reading-grid"><aside class="ml-outline"><strong>${jt('На этой странице', 'Осы бетте')}</strong><nav aria-label="${jt('Темы недели', 'Апта тақырыптары')}">${week.topics.map((topic, i) => `<button type="button" data-ml-jump="${i + 1}">${i + 1}. ${escapeHTML(topic.title)}</button>`).join('')}<button type="button" data-ml-jump="assignment">${jt('Самостоятельная работа', 'Өзіндік жұмыс')}</button></nav><a class="sources" href="#course/labs">${jt('Все лабораторные', 'Барлық зертхана')} ↗</a></aside>
    <div class="ml-reading-body">
      <section class="ml-objectives"><h2>${jt('Чему ты научишься', 'Не үйренесің')}</h2><ul>${week.goals.map(goal => `<li>${escapeHTML(goal)}</li>`).join('')}</ul></section>
      <section class="ml-downloads"><h2>${jt('Повтори опыт в Python', 'Тәжірибені Python-да қайтала')}</h2>
      <p>${jt('В браузере можно сравнить готовые расчёты. Скачай архив, распакуй его и запусти lab.py, чтобы менять параметры и получать собственные результаты.', 'Браузерде дайын есептеулерді салыстыруға болады. Параметрлерді өзгертіп, өз нәтижеңді алу үшін архивті жүктеп, ашып, lab.py файлын іске қос.')}</p>
      <pre><code>python -m pip install -r requirements.txt\npython lab.py &gt; results.json</code></pre>
      <div class="hero-actions"><a class="button outline" href="ml/${id}/lab.zip" download>${jt('Скачать лабораторную', 'Зертхананы жүктеу')} ZIP ↓</a><a class="sources" href="ml/${id}/lab.py" download>lab.py ↓</a>${lesson.assets.map(file => `<a class="sources" href="ml/${id}/${file}" download>${escapeHTML(file)} ↓</a>`).join('')}</div>
      <details class="ml-code" data-source="ml/${id}/lab.py"><summary>${jt('Посмотреть Python-код', 'Python кодын қарау')}</summary><pre><code></code></pre></details></section>
      ${week.topics.map((topic, index) => mlTopicHTML(topic, data.topics[index], index)).join('')}
      <section class="ml-assignment" id="ml-topic-assignment" tabindex="-1"><h2>${jt('Самостоятельная работа', 'Өзіндік жұмыс')}</h2><p>${escapeHTML(week.assignment)}</p>
      ${project ? `<p><strong>${jt('Отложенный тест', 'Соңғы тест')}</strong> · ROC-AUC ${escapeHTML(data.heldOutAUC)} · ${jt('базовый вариант', 'базалық нұсқа')} ${escapeHTML(data.baselineAUC)}</p>` : ''}
      <label for="ml-note">${jt('Мой отчёт и заметки', 'Менің есебім мен жазбам')}</label><textarea id="ml-note" rows="5" maxlength="10000"></textarea><small class="ml-save" role="status"></small></section>
      <details class="ml-sources"><summary>${jt('Материалы, на которых основан урок', 'Сабақтың бастапқы материалдары')}</summary><ul>${lesson.sources.map(source => `<li>${escapeHTML(source)}</li>`).join('')}</ul></details>
      <nav class="lesson-nav" aria-label="${jt('Переход между неделями', 'Апталар арасында өту')}">
        <a class="button outline" href="${project ? mlWeekHref('14') : number > 1 ? adjacent(-1) : '#course'}">← ${project || number > 1 ? jt('Предыдущая неделя', 'Алдыңғы апта') : jt('Программа', 'Бағдарлама')}</a>
        ${project ? '' : `<button class="button outline" id="ml-complete" type="button"></button><a class="button" href="${number < 14 ? adjacent(1) : '#course/project'}">${number < 14 ? jt('Следующая неделя', 'Келесі апта') : jt('Итоговый практикум', 'Қорытынды практикум')} →</a>`}</nav>
    </div></div></article>`;

  main.querySelectorAll('[data-ml-jump]').forEach(button => button.onclick = () => {
    const section = main.querySelector(`#ml-topic-${button.dataset.mlJump}`);
    section.scrollIntoView({block: 'start'});
    section.focus({preventScroll: true});
  });
  const redraw = new Map();
  mlPlotObserver = new ResizeObserver(entries => entries.forEach(entry => redraw.get(entry.target)()));
  week.topics.forEach((topic, index) => {
    const n = index + 1, key = `${id}/${n}`, cases = data.topics[index];
    mlBindLab(main.querySelector(`[data-ml-topic="${n}"]`), cases, topic, record, key, lesson.independentAxes?.includes(n), redraw);
    mlBindQuiz(main.querySelector(`[data-ml-quiz="${n}"]`), topic, record, key);
  });
  mlBindNote(main.querySelector('#ml-note'), 'notes', id, record.notes[id]);
  mlBindCode(main.querySelector('.ml-code'));
  if (!project) mlBindCompletion(main.querySelector('#ml-complete'), id);
}

function mlBindNote(input, field, key, value) {
  input.value = value ?? '';
  input.addEventListener('input', () => {
    const current = MLStore.get().mlSemester[field];
    const saved = MLStore.mlUpdate({[field]: {...current, [key]: input.value}});
    input.nextElementSibling.textContent = saved ? jt('Сохранено на устройстве', 'Құрылғыда сақталды') : jt('Сохранено до закрытия страницы', 'Бет жабылғанша сақталды');
  });
}

function mlBindLab(section, cases, topic, record, key, independentAxes, redraw) {
  const select = section.querySelector('select');
  const output = section.querySelector('.ml-chart-output');
  const caption = section.querySelector('figcaption');
  const points = section.querySelector('.ml-points');
  const table = points.querySelector('.ml-table');
  const drawTable = () => {
    table.innerHTML = points.open ? mlChartTable(cases[Number(select.value)], topic) : '';
  };
  const width = () => Math.max(195, Math.min(590, output.clientWidth - 10));
  let drawnWidth;
  const drawPlot = () => {
    const current = cases[Number(select.value)];
    drawnWidth = width();
    output.innerHTML = mlPlot(cases, current, topic, independentAxes, drawnWidth);
  };
  const draw = () => {
    const current = cases[Number(select.value)];
    drawPlot();
    caption.textContent = mlText(current.note) + (independentAxes ? ` ${jt('Шкала пересчитывается для каждого условия.', 'Шкала әр шартқа қайта есептеледі.')}` : '');
    drawTable();
  };
  select.addEventListener('change', draw);
  points.addEventListener('toggle', drawTable);
  mlBindNote(section.querySelector('textarea'), 'practice', key, record.practice[key]);
  redraw.set(output, () => { if (drawnWidth !== width()) drawPlot(); });
  mlPlotObserver.observe(output);
  draw();
}

function mlBindQuiz(quiz, topic, record, key) {
  const buttons = [...quiz.querySelectorAll('button')], feedback = quiz.querySelector('.ml-feedback');
  const draw = answer => {
    buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === answer)));
    if (answer === undefined) return;
    const correct = answer === topic.answer;
    feedback.textContent = correct ? `${jt('Верно.', 'Дұрыс.')} ${topic.feedback}` : jt('Попробуй ещё раз. Сверь ответ с примером и графиком.', 'Қайта байқап көр. Жауабыңды мысалмен және графикпен салыстыр.');
    feedback.dataset.correct = String(correct);
  };
  buttons.forEach((button, i) => button.onclick = () => {
    const answers = MLStore.get().mlSemester.answers;
    const saved = MLStore.mlUpdate({answers: {...answers, [key]: i}});
    draw(i);
    if (!saved) toast(jt('Ответ сохранён до закрытия страницы', 'Жауап бет жабылғанша сақталды'));
  });
  draw(record.answers[key]);
}

function mlBindCode(details) {
  const code = details.querySelector('code');
  let loaded = false;
  details.addEventListener('toggle', async () => {
    if (!details.open || loaded) return;
    code.textContent = jt('Загрузка…', 'Жүктелуде…');
    try {
      const response = await fetch(details.dataset.source, {signal: AbortSignal.timeout(8000)});
      if (!response.ok) throw new Error('Python source unavailable');
      code.textContent = await response.text();
      loaded = true;
    } catch {
      code.textContent = jt('Код не загрузился. Открой блок ещё раз или скачай архив.', 'Код жүктелмеді. Блокты қайта аш немесе архивті жүкте.');
    }
  });
}

function mlBindCompletion(button, id) {
  const draw = done => {
    button.setAttribute('aria-pressed', String(done));
    button.textContent = done ? jt('Пройдено ✓', 'Аяқталды ✓') : jt('Отметить пройденной', 'Аяқталды деп белгілеу');
  };
  draw(MLStore.get().mlSemester.completed.includes(id));
  button.onclick = () => {
    const {completed} = MLStore.get().mlSemester, done = completed.includes(id);
    const saved = MLStore.mlUpdate({completed: done ? completed.filter(week => week !== id) : [...completed, id]});
    draw(!done);
    if (!saved) toast(jt('Отметка сохранена до закрытия страницы', 'Белгі бет жабылғанша сақталды'));
  };
}
