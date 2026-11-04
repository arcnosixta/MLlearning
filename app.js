const main=document.querySelector('main');
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function toast(s){const el=document.querySelector('#toast');el.textContent=s;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2300)}

async function route() {
  const hash = location.hash;
  const [, section, id] = hash.split('/');
  mlPlotObserver?.disconnect();
  mlPythonDispose?.();
  mlPythonDispose = undefined;
  clearInterval(examTimer);
  clearInterval(trackExamTimer);
  if (hash === '#sysadmin/review') await renderSysadminReview();
  else if (hash === '#sysadmin/full' || hash.startsWith('#sysadmin/topic/')) await renderSysadminFull(id);
  else if (hash === '#java/full' || hash.startsWith('#java/topic/')) await renderJavaFull(id);
  else if (hash === '#course' || hash.startsWith('#course/')) await renderML(section, id);
  else if (hash === '#lab') await renderML('labs');
  else if (/^#(?:lesson|files)(?:\/|$)|^#learn\/(?:ml|files)(?:\/|$)/.test(hash)) await renderML('legacy');
  else if (hash.startsWith('#learn/')) await renderTeaching(section, id);
  else if (hash.startsWith('#track/')) await renderTrack(section, id);
  else if (hash === '#java' || hash.startsWith('#java/week/')) await renderJava(id);
  else if (hash === '#exams' || hash.startsWith('#exam/')) await renderExams(section);
  else if (hash === '#progress') await renderStudioProgress();
  else if (hash === '#prepare') await renderStudioPrepare();
  else if (hash === '#data') renderData();
  else await renderLibrary();
  if (location.hash !== hash) return;
  await enhanceTeaching(hash).catch(() => {
    if (hash === location.hash) toast(jt('Учебный разбор не загрузился. Обнови страницу.', 'Оқу талдауы жүктелмеді. Бетті жаңарт.'));
  });
  if (location.hash !== hash) return;
  enhanceStudio(hash);
  if (hash !== '#catalog') window.scrollTo(0, 0);
}

function startRoute(initial = false) {
  const requested = location.hash;
  return navigateStudio(initial).catch(() => {
    if (requested === location.hash) fullCourseFailure('#catalog');
  });
}

window.addEventListener('hashchange', () => startRoute());
queueMicrotask(() => startRoute(true));
