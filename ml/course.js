const mlText = value => value?.[window.ML_LOCALE === 'kk' ? 'kk' : 'ru'];
const mlWeekHref = id => id === 'project' ? '#course/project' : `#course/week/${id}`;

function mlCoursePage(index, mode) {
  const labs = mode === 'labs', record = MLStore.get().mlSemester;
  const next = record.lastWeek ?? index.weeks.find(week => !record.completed.includes(week.id))?.id ?? '01';
  main.innerHTML = `<section class="tracks-page ml-course">
    <a class="breadcrumb" href="${labs ? '#course' : '#catalog'}">← ${labs ? jt('Программа курса', 'Курс бағдарламасы') : jt('Все направления', 'Барлық бағыттар')}</a>
    <div class="ml-course-hero"><div class="eyebrow">ML 3305 / 2026–2027</div>
    <h1>${labs ? jt('Лабораторные по машинному обучению', 'Машиналық оқыту зертханалары') : jt('Машинное обучение', 'Машиналық оқыту')}</h1>
    <p>${labs ? jt('Выбери эксперимент, сравни результаты на графике и повтори расчёт в Python.', 'Тәжірибені таңдап, нәтижені графикте салыстыр және есептеуді Python-да қайтала.') : jt('Четырнадцать недель от первой таблицы в Python до обнаружения объектов. Читай объяснения, меняй условия опыта и проверяй выводы на данных.', 'Python-дағы алғашқы кестеден нысандарды анықтауға дейінгі он төрт апта. Түсіндірмені оқы, тәжірибе шартын өзгертіп, қорытындыңды дерекпен тексер.')}</p>
    <div class="hero-actions"><a class="button" href="${mlWeekHref(next)}">${record.lastWeek ? jt('Продолжить обучение', 'Оқуды жалғастыру') : jt('Начать с недели 1', '1-аптадан бастау')} →</a>
    <a class="button outline" href="${labs ? '#course' : '#course/labs'}">${labs ? jt('Вся программа', 'Толық бағдарлама') : jt('Все лабораторные', 'Барлық зертхана')} ↗</a></div></div>
    ${mode === 'legacy' ? `<p class="callout">${jt('По этой ссылке раньше открывались материалы прежнего курса. Выбери нужную тему в новой программе.', 'Бұл сілтеме бұрынғы курс материалдарын ашатын. Жаңа бағдарламадан қажетті тақырыпты таңда.')}</p>` : ''}
    <div class="ml-course-tools"><p>${record.completed.length} / ${index.weeks.length} ${jt('недель пройдено', 'апта аяқталды')}</p><label for="ml-search">${jt('Поиск по программе', 'Бағдарламадан іздеу')}</label><input class="search" id="ml-search" type="search" placeholder="${jt('Например, ROC или YOLO', 'Мысалы, ROC немесе YOLO')}"></div>
    <ol class="ml-weeks" id="ml-weeks"></ol>
    <section class="ml-project-card"><div class="eyebrow">${jt('ПОСЛЕ 14-Й НЕДЕЛИ', '14-АПТАДАН КЕЙІН')}</div><h2>${escapeHTML(mlText(index.project.title))}</h2><p>${escapeHTML(mlText(index.project.intro))}</p><a class="button outline" href="#course/project">${jt('Открыть итоговый практикум', 'Қорытынды практикумды ашу')} →</a></section>
  </section>`;
  const search = main.querySelector('#ml-search');
  const draw = () => {
    const query = search.value.trim().toLocaleLowerCase();
    const matches = index.weeks.filter(week => [mlText(week.title), ...mlText(week.topics)].some(text => text.toLocaleLowerCase().includes(query)));
    main.querySelector('#ml-weeks').innerHTML = matches.map(week => `<li>
      <span class="ml-week-index">${week.id}${record.completed.includes(week.id) ? ' ✓' : ''}</span>
      <div><h2><a href="${mlWeekHref(week.id)}">${escapeHTML(mlText(week.title))}</a></h2>
      <p>${mlText(week.topics).map(escapeHTML).join(' · ')}</p></div>
      ${labs ? `<a class="sources" href="ml/${week.id}/lab.zip" download aria-label="${jt('Скачать лабораторную', 'Зертхананы жүктеу')} ${week.id}">ZIP ↓</a>` : `<a class="ml-week-arrow" href="${mlWeekHref(week.id)}" aria-label="${jt('Открыть неделю', 'Аптаны ашу')} ${week.id}">→</a>`}
    </li>`).join('') || `<li>${jt('Темы с таким названием не найдены.', 'Мұндай атауы бар тақырып табылмады.')}</li>`;
  };
  search.addEventListener('input', draw);
  draw();
}

async function renderML(mode, id) {
  const requested = location.hash;
  try {
    if (mode === 'week' && !/^(0[1-9]|1[0-4])$/.test(id ?? '')) {
      main.innerHTML = `<section class="tracks-page"><h1>${jt('Неделя не найдена', 'Апта табылмады')}</h1><a class="button" href="#course">${jt('К программе', 'Бағдарламаға')} →</a></section>`;
      return;
    }
    if (mode === 'week' || mode === 'project') {
      const section = mode === 'project' ? 'project' : id;
      const base = `ml/${section}`;
      const [lesson, data] = await Promise.all([fullCourseJSON(`${base}/lesson.json`), fullCourseJSON(`${base}/results.json`)]);
      if (requested === location.hash) mlWeekPage(lesson, data);
    } else {
      const index = await fullCourseJSON('ml/index.json');
      if (requested === location.hash) mlCoursePage(index, mode);
    }
  } catch {
    if (requested === location.hash) fullCourseFailure('#course');
  }
}
