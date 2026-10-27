/* Optional, untimed scenario review. It never completes a video or practical topic. */
function sysadminReviewHTML(question,href){
  const text=sysadminFullText(question);
  return `<form class="sysadmin-review" data-review="${question.id}"><fieldset><legend>${escapeHTML(text.question)}</legend>${text.options.map((option,i)=>`<label><input type="radio" name="review-${question.id}" value="${i}" required><span>${escapeHTML(option)}</span></label>`).join('')}</fieldset><button class="button outline" type="submit">${jt('Проверить ответ','Жауапты тексеру')}</button><p class="sysadmin-review-feedback" role="status"></p>${href?`<a class="sources" href="${href}">${jt('Повторить тему','Тақырыпты қайталау')} →</a>`:''}</form>`;
}
function bindSysadminReview(container,questions){
  for(const question of questions){
    const form=container.querySelector('[data-review="'+question.id+'"]');if(!form)continue;
    const feedback=form.querySelector('.sysadmin-review-feedback'),key='sysadmin/'+question.id;
    function show(answer){const correct=answer===question.answer;feedback.dataset.correct=String(correct);feedback.textContent=(correct?jt('Верно. ','Дұрыс. '):jt('Стоит повторить. ','Қайталау керек. '))+sysadminFullText(question).explanation}
    const saved=MLStore.get().learning.review[key];if(saved!==undefined){form.querySelector('input[value="'+saved+'"]').checked=true;show(saved)}
    form.onsubmit=event=>{event.preventDefault();const selected=form.querySelector('input:checked');if(!selected)return;const answer=Number(selected.value),current=MLStore.get().learning;const stored=MLStore.learningUpdate({review:{...current.review,[key]:answer}});show(answer);if(!stored)feedback.textContent+=' '+jt('Ответ останется только до закрытия страницы.','Жауап бет жабылғанша ғана қалады.');const score=document.querySelector('#sysadmin-review-score');if(score){const state=MLStore.get().learning.review,answered=questions.filter(q=>state['sysadmin/'+q.id]!==undefined).length,correct=questions.filter(q=>state['sysadmin/'+q.id]===q.answer).length;score.textContent=jt('Отвечено','Жауап берілді')+': '+answered+'/'+questions.length+' · '+jt('Верно','Дұрыс')+': '+correct}};
  }
}
async function renderSysadminReview(){
  const requested=location.hash;let questions,data;
  try{[questions,data]=await Promise.all([fullCourseJSON('sysadmin-full/review.json'),sysadminFullData()])}catch{if(requested===location.hash)fullCourseFailure('#sysadmin/full');return}
  if(requested!==location.hash)return;
  const state=MLStore.get().learning.review,answered=questions.filter(q=>state['sysadmin/'+q.id]!==undefined).length,correct=questions.filter(q=>state['sysadmin/'+q.id]===q.answer).length;
  main.innerHTML=`<section class="tracks-page sysadmin-full"><a class="sources" href="#sysadmin/full">← ${jt('Весь курс Linux','Толық Linux курсы')}</a><h1>${jt('Проверь решения в35 ситуациях','35 жағдайдағы шешімді тексер')}</h1><p>${jt('По одному сценарию на тему, без таймера. Ответы и объяснения доступны сразу после проверки; это учебная самопроверка, её результаты не меняют отметки видео и практики.','Әр тақырыпқа бір жағдай, таймер жоқ. Тексерген соң жауап пен түсіндірме ашылады. Бұл өзін тексеру, нәтижелер бейне және тәжірибе белгілерін өзгертпейді.')}</p><p id="sysadmin-review-score" role="status">${jt('Отвечено','Жауап берілді')}: ${answered}/${questions.length} · ${jt('Верно','Дұрыс')}: ${correct}</p>${questions.map(q=>{const first=data.entries.find(entry=>entry.guideId===q.id);return sysadminReviewHTML(q,'#sysadmin/topic/'+first.courseId)}).join('')}</section>`;
  bindSysadminReview(main,questions);
}
