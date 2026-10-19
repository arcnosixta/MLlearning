/* Shared by storage, curriculum and assessment UI, before either locale loads. */
(()=>{
  const range=(start,end)=>Array.from({length:end-start+1},(_,i)=>start+i);
  const control=(count,minutes,weeks,ru,kk,legacy=false)=>Object.freeze({count,minutes,weeks:Object.freeze(weeks),ru,kk,legacy});
  const controls=Object.freeze({
    rk1:control(30,45,range(1,7),'РК-1','РК-1'),
    rk2:control(30,45,range(8,13),'РК-2','РК-2'),
    session:control(60,90,range(1,13),'Пробная сессия','Сынақ сессиясы'),
    // Retained for saved attempts and old public links, with their original banks.
    mid:control(15,20,range(1,3),'Прежняя рубежная проверка','Бұрынғы аралық тексеру',true),
    final:control(30,40,range(1,6),'Прежняя итоговая проверка','Бұрынғы қорытынды тексеру',true)
  });
  window.IMTrackConfig=Object.freeze({weeks:13,lessonIds:Object.freeze(range(1,13).map(n=>String(n).padStart(2,'0'))),controls,kinds:Object.freeze(['rk1','rk2','session'])});
})();
