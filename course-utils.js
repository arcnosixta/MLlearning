/* Shared reader infrastructure: failed requests remain retryable. */
const fullCourseRequests=new Map();
function fullCourseJSON(url){
  if(!fullCourseRequests.has(url)){
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
    const request=fetch(url,{signal:controller.signal}).then(response=>{if(!response.ok)throw new Error('Course response '+response.status);return response.json()}).catch(error=>{fullCourseRequests.delete(url);throw error}).finally(()=>clearTimeout(timer));
    fullCourseRequests.set(url,request);
  }
  return fullCourseRequests.get(url);
}
function fullCourseFailure(back){
  main.innerHTML=`<section class="tracks-page" role="status"><h1>${jt('Материал пока не загрузился','Материал әзірге жүктелмеді')}</h1><p>${jt('Проверь соединение и попробуй ещё раз. Сохранённые решения остаются на устройстве.','Байланысты тексеріп, қайта көр. Сақталған шешімдер құрылғыда қалады.')}</p><button class="button" id="full-course-retry">${jt('Повторить загрузку','Қайта жүктеу')}</button> <a class="sources" href="${back}">${jt('К программе курса','Курс бағдарламасына')} →</a></section>`;
  main.querySelector('#full-course-retry').onclick=()=>navigateStudio(true).catch(()=>{});
}
function fullCourseFilters(prefix,defaults){
  const params=new URL(location.href).searchParams;
  return Object.fromEntries(Object.entries(defaults).map(([key,value])=>[key,(params.get(prefix+'_'+key)||value).slice(0,256)]));
}
function fullCourseSaveFilters(prefix,values){
  const url=new URL(location.href);
  for(const [key,value] of Object.entries(values)){if(value&&value!=='all')url.searchParams.set(prefix+'_'+key,value);else url.searchParams.delete(prefix+'_'+key)}
  history.replaceState(history.state,'',url.pathname+url.search+url.hash);
  document.querySelectorAll('.language-switch a').forEach(link=>{const next=new URL(url);next.searchParams.set('lang',link.lang);link.href=next.pathname+next.search+next.hash});
}
function bindFullCompletion(button,key,labels,status){
  function draw(){const done=MLStore.get().learning.completed.includes(key);button.textContent=labels[done?1:0];button.setAttribute('aria-pressed',String(done))}
  draw();button.onclick=()=>{const current=MLStore.get().learning,done=current.completed.includes(key),completed=done?current.completed.filter(value=>value!==key):[...current.completed,key];const stored=MLStore.learningUpdate({completed});draw();if(status)status.textContent=stored?jt('Отметка сохранена','Белгі сақталды'):jt('Хранилище недоступно: отметка останется только до закрытия страницы.','Сақтау қолжетімсіз: белгі бет жабылғанша ғана қалады.')};
}
function focusFullCourseHeading(){
  if(!/^#(?:java|sysadmin)\/(?:full|review|topic\/)/.test(location.hash))return;
  const heading=main.querySelector('h1');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true})}
}
