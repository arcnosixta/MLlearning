/* Complete textbook route; the semester and its exam IDs remain stable. */
function javaFullData(){return fullCourseJSON('java-full/index.json')}
async function renderJavaFull(id){
  const requested=location.hash;let chapters;try{chapters=await javaFullData()}catch{if(requested===location.hash)fullCourseFailure('#java/full');return}if(requested!==location.hash)return;
  const lang=window.ML_LOCALE==='kk'?'kk':'ru',record=window.MLStore.get().learning;
  if(!id){
    const completed=chapters.filter(c=>record.completed.includes('java-full/'+c.id)).length;
    main.innerHTML=`<section class="java-page java-full"><a class="course-home-link" href="#java">← ${jt('Семестр Java','Java семестрі')}</a><div class="eyebrow">JAVA / ${jt('ПОЛНЫЙ КУРС','ТОЛЫҚ КУРС')}</div><h1>${jt('Java: от первой программы до приложения.','Java: алғашқы бағдарламадан қосымшаға дейін.')}</h1><p class="lesson-intro">${jt('Подробные главы по книге Java from EPAM, двум презентациям и сборнику задач. Теория, запускаемый код, три задачи с разбором и самопроверка в каждой главе.','Java from EPAM кітабы, екі презентация және есептер жинағы бойынша толық тараулар. Әр тарауда теория, іске қосылатын код, шешімі бар үш есеп және өзін тексеру.')}</p><p>${jt('Пройдено','Аяқталды')}: ${completed} / ${chapters.length} · Java 17+ · RU / ҚАЗ</p><p>${jt('Сначала прочитай объяснение, предскажи вывод и запусти Main.java. Решай задачи до открытия разбора. Ответы сохраняются на этом устройстве и входят в экспорт данных.','Алдымен түсіндірмені оқып, нәтижені болжа және Main.java орында. Талдауды ашпай есепті шеш. Жауаптар осы құрылғыда сақталып, деректер экспортына кіреді.')}</p><p><a class="sources" href="java-full/study.zip" download>${jt('Скачать весь учебный архив Java (ZIP)','Java оқу архивін толық жүктеу (ZIP)')} ↗</a></p><div class="java-controls"><a class="chip" href="#java">${jt('14 недель и РК','14 апта және РК')}</a><a class="chip" href="#track/java-advanced">${jt('Углублённая практика','Тереңдетілген тәжірибе')}</a></div><div class="java-full-tools"><label>${jt('Поиск по главам','Тарау іздеу')}<input class="search" id="java-full-search" type="search"></label><label>${jt('Прогресс','Ілгерілеу')}<select id="java-full-progress"><option value="all">${jt('Все главы','Барлық тарау')}</option><option value="todo">${jt('Ещё не пройдены','Әлі аяқталмаған')}</option><option value="done">${jt('Пройденные','Аяқталған')}</option></select></label></div><p><a class="button" id="java-full-next"></a></p><p id="java-full-count" role="status"></p><div class="week-grid">${chapters.map(c=>`<a class="week-card ${record.completed.includes('java-full/'+c.id)?'done':''}" href="#java/topic/${c.id}"><span class="eyebrow">${jt('Глава','Тарау')} ${c.id}</span><h3>${escapeHTML(c[lang].title)}</h3><p>${escapeHTML(c[lang].description)}</p><div class="week-bottom"><span>${jt('Теория · код · 3 задачи','Теория · код · 3 есеп')}</span><span>${record.completed.includes('java-full/'+c.id)?'✓':'↗'}</span></div></a>`).join('')}</div></section>`;
    const search=main.querySelector('#java-full-search'),progress=main.querySelector('#java-full-progress'),filters=fullCourseFilters('java',{q:'',progress:'all'});
    search.value=filters.q;progress.value=['todo','done'].includes(filters.progress)?filters.progress:'all';
    const cards=[...main.querySelectorAll('.week-card')];
    function draw(){let count=0;const current=MLStore.get().learning;fullCourseSaveFilters('java',{q:search.value,progress:progress.value});const query=search.value.toLocaleLowerCase().trim();cards.forEach((card,i)=>{const c=chapters[i],done=current.completed.includes('java-full/'+c.id),visible=(!query||(c[lang].title+' '+c[lang].description).toLocaleLowerCase().includes(query))&&(progress.value==='all'||(progress.value==='done'?done:!done));card.hidden=!visible;if(visible)count++});const first=cards.find((card,i)=>!card.hidden&&!current.completed.includes('java-full/'+chapters[i].id))||cards.find(card=>!card.hidden),next=main.querySelector('#java-full-next');next.hidden=!first;if(first){next.href=first.getAttribute('href');next.textContent=jt('Перейти к следующей главе','Келесі тарауға өту')}main.querySelector('#java-full-count').textContent=jt('Показано','Көрсетілген')+': '+count+' / '+chapters.length}
    search.oninput=draw;progress.onchange=draw;draw();
    return;
  }
  const index=chapters.findIndex(c=>c.id===id);let chapter=chapters[index];if(chapter){try{chapter=await fullCourseJSON('java-full/'+id+'/chapter.json')}catch{if(requested===location.hash)fullCourseFailure('#java/full');return}if(requested!==location.hash)return;}
  if(!chapter){main.innerHTML=`<section class="java-page"><h1>${jt('Глава не найдена','Тарау табылмады')}</h1><a class="button" href="#java/full">${jt('Все главы','Барлық тарау')} →</a></section>`;return}
  const key='java-full/'+id,text=chapter[lang];
  // HTML is generated and sanitized at build time; user input is assigned through .value.
  const body=text.html.replace(/\{\{answer:([123])\}\}/g,(_,n)=>`<label for="java-full-answer-${n}">${jt('Твоё решение','Сенің шешімің')} ${n}</label><textarea id="java-full-answer-${n}" class="java-note" data-full-answer="${key}/${n}" rows="5" maxlength="10000"></textarea>`);
  main.innerHTML=`<div class="java-layout java-full"><aside class="java-sidebar"><a href="#java/full">← ${jt('Полная программа','Толық бағдарлама')}</a>${chapters.map(c=>`<a href="#java/topic/${c.id}" ${c.id===id?'class="active" aria-current="page"':''}>${c.id}. ${escapeHTML(c[lang].title)}</a>`).join('')}</aside><article class="java-lesson java-full-article"><a class="course-home-link" href="#java/full">← ${jt('Все главы','Барлық тарау')}</a><h1>${escapeHTML(text.title)}</h1><div class="java-meta"><span>Java 17+</span><span>${jt('Глава','Тарау')} ${id} / ${chapters.length}</span></div><p>${jt('Нужно знать','Алдын ала білу')}: ${escapeHTML(chapter[lang==='ru'?'requiresRu':'requiresKk'])}</p><a class="sources" href="java-full/${id}/Main.java" download>${jt('Скачать пример Main.java','Main.java мысалын жүктеу')} ↗</a><div class="java-full-content">${body}</div>${chapter.lab?`<p><a class="sources" href="${chapter.lab}" download>${jt('Скачать Maven-лабораторную (ZIP)','Maven зертханасын жүктеу (ZIP)')} ↗</a></p>`:''}<p class="learning-save-status" role="status"></p><h2>${jt('Материалы к главе','Тарау материалдары')}</h2><ul>${chapter.references.map(r=>`<li>${escapeHTML(r)}</li>`).join('')}</ul><p><a class="sources" href="${escapeHTML(chapter.docs)}" target="_blank" rel="noopener">${jt('Документация Java','Java құжаттамасы')} ↗</a></p><div class="lesson-nav">${index?`<a class="button outline" href="#java/topic/${chapters[index-1].id}">← ${jt('Назад','Артқа')}</a>`:'<a class="button outline" href="#java/full">← Java</a>'}<button class="button green" id="java-full-complete">${record.completed.includes(key)?jt('Пройдено ✓','Аяқталды ✓'):jt('Я могу решить задачи','Есептерді шеше аламын')}</button>${index<chapters.length-1?`<a class="button" href="#java/topic/${chapters[index+1].id}">${jt('Следующая глава','Келесі тарау')} →</a>`:'<a class="button" href="#java/full">Java →</a>'}</div></article></div>`;
  const status=main.querySelector('.learning-save-status');
  main.querySelectorAll('[data-full-answer]').forEach(input=>{
    input.value=record.practice[input.dataset.fullAnswer]||'';
    input.oninput=()=>{const current=window.MLStore.get().learning;const saved=window.MLStore.learningUpdate({practice:{...current.practice,[input.dataset.fullAnswer]:input.value}});status.textContent=saved?jt('Решение сохранено','Шешім сақталды'):jt('Не удалось сохранить. Не закрывай страницу.','Сақтау мүмкін емес. Бетті жаппа.')};
  });
  bindFullCompletion(main.querySelector('#java-full-complete'),key,[jt('Отметить главу пройденной','Тарауды аяқталды деп белгілеу'),jt('Пройдено ✓ · отменить','Аяқталды ✓ · алып тастау')],status);
}

async function enhanceJavaFull(hash){
  const week=hash.match(/^#(?:java\/week|learn\/java)\/(\d{2})$/);
  const advanced=hash.match(/^#(?:track|learn)\/java-advanced\/(\d{2})$/);
  const overview=hash==='#java'||hash==='#track/java-advanced';
  if(!week&&!advanced&&!overview&&!['','#catalog','#progress'].includes(hash))return;
  const chapters=await javaFullData();if(hash!==location.hash)return;
  const lang=window.ML_LOCALE==='kk'?'kk':'ru',learning=MLStore.get().learning;
  if(hash===''||hash==='#catalog'){
    main.querySelectorAll('[data-course-id="java"],[data-course-id="java-advanced"]').forEach(card=>{
      if(card.querySelector('.java-full-link'))return;
      const links=card.querySelector('.catalog-links')||card.appendChild(Object.assign(document.createElement('div'),{className:'catalog-links'}));
      const link=document.createElement('a');link.className='sources java-full-link';link.href='#java/full';link.textContent=jt('Полный курс · 26 глав →','Толық курс · 26 тарау →');links.append(link);
    });return;
  }
  if(main.querySelector('.java-full-links,.java-full-banner'))return;
  const completed=chapters.filter(c=>learning.completed.includes('java-full/'+c.id)).length;
  const target=week||advanced?main.querySelector('.java-lesson,.teaching-page'):hash==='#progress'?main.querySelector('.studio-dashboard'):main.querySelector('.java-page,.tracks-page');
  if(!target)return;
  const block=document.createElement('aside');
  if(week||advanced){
    const number=Number((week||advanced)[1]),related=chapters.filter(c=>(week?c.weeks:c.advanced).includes(number));
    block.className='java-full-links callout';
    block.innerHTML=`<h2>${jt('Подробно по этой теме','Тақырыпты толық оқу')}</h2><ul>${related.map(c=>`<li><a class="sources" href="#java/topic/${c.id}">${escapeHTML(c[lang].title)} →</a></li>`).join('')}</ul><a class="sources" href="#java/full">${jt('Все 26 глав','Барлық 26 тарау')} →</a>`;
    const intro=target.querySelector('.lesson-intro,.teaching-goal');if(intro)intro.after(block);else target.append(block);
  }else{
    block.className='teaching-start java-full-banner';
    block.innerHTML=`<div><strong>${jt('Полный Java-курс по твоим материалам','Материалдарың бойынша толық Java курсы')}</strong><p>${jt('26 глав: подробная теория, код, задачи и разборы. От типов и ООП до JDBC, сетей, XML и GUI.','26 тарау: толық теория, код, есептер және шешімдер. Типтер мен ООП-тан JDBC, желі, XML және GUI-ге дейін.')} ${jt('Пройдено','Аяқталды')}: ${completed}/26.</p></div><a class="button" href="#java/full">${jt('Открыть полный курс','Толық курсты ашу')} ↗</a>`;
    const heading=target.querySelector('h1');if(heading)heading.after(block);else target.prepend(block);
  }
}
