/* A deterministic short-answer trainer. This is not a Java compiler or shell. */
(()=>{
  const normalize=s=>s.trim().replace(/\s+/g,'');
  window.IMTerminal={
    check:(input,accepted)=>accepted.some(answer=>normalize(input)===normalize(answer)),
    mount:(container,exercise,lang,onSuccess)=>{
      const kk=lang==='kk',t=exercise[kk?'kk':'ru'];
      container.innerHTML=`<div class="terminal-box"><h3>${kk?'Жауаптар терминалы':'Терминал ответов'}</h3><p>${kk?'Қысқа жауапты не пәрменді енгіз. Бұл Java компиляторы емес; жауап тапсырма шартымен тексеріледі.':'Введи короткий ответ или команду. Это не компилятор Java: ответ проверяется по условию задания.'}</p><p class="terminal-prompt"></p><form><label for="terminal-input">${kk?'Сенің жауабың':'Твой ответ'}</label><input id="terminal-input" maxlength="300" autocomplete="off" spellcheck="false"><div class="java-controls"><button class="button" type="submit">${kk?'Тексеру':'Проверить'}</button><button class="button outline" type="button" id="terminal-hint">${kk?'Көмек':'Подсказка'}</button><button class="button outline" type="button" id="terminal-reset">${kk?'Тазалау':'Очистить'}</button></div></form><div class="terminal-result" role="status" aria-live="polite"></div></div>`;
      container.querySelector('.terminal-prompt').textContent=t.prompt;
      const input=container.querySelector('input'),result=container.querySelector('.terminal-result');
      container.querySelector('form').onsubmit=e=>{e.preventDefault();if(!input.value.trim()){result.textContent=kk?'Алдымен жауап енгіз.':'Сначала введи ответ.';return}const ok=window.IMTerminal.check(input.value,exercise.answers);result.textContent=ok?(kk?'Дұрыс. Енді шешімді дауыстап түсіндір.':'Верно. Теперь объясни решение вслух.'):(kk?'Әзірге дұрыс емес. Синтаксис пен регистрді тексер немесе көмекті аш.':'Пока неверно. Проверь синтаксис и регистр или открой подсказку.');result.dataset.correct=String(ok);if(ok)onSuccess?.()};
      container.querySelector('#terminal-hint').onclick=()=>{result.textContent=t.hint};
      container.querySelector('#terminal-reset').onclick=()=>{input.value='';result.textContent='';delete result.dataset.correct;input.focus()};
    }
  };
})();
