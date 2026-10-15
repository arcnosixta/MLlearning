/* Choose a single locale before loading the application; URLs remain shareable. */
(()=>{
  const requested=new URLSearchParams(location.search).get('lang');
  let saved;try{saved=localStorage.getItem('mllearning-language')}catch{}
  const lang=['ru','kk'].includes(requested)?requested:saved==='kk'?'kk':'ru';
  window.ML_LOCALE=lang;
  document.documentElement.lang=lang;
  try{localStorage.setItem('mllearning-language',lang)}catch{}
  document.addEventListener('DOMContentLoaded',async()=>{
    if(lang==='kk'){
      const response=await fetch('ui.kk.json');
      if(!response.ok)throw new Error('Locale unavailable');
      const dictionary=await response.json();
      const keys=Object.keys(dictionary).sort((a,b)=>b.length-a.length);
      const translate=s=>{let out='',i=0;while(i<s.length){const key=keys.find(k=>s.startsWith(k,i));if(key){out+=dictionary[key];i+=key.length}else out+=s[i++]}return out};
      const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
      const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
      nodes.forEach(n=>{if(!['SCRIPT','STYLE'].includes(n.parentElement.tagName))n.textContent=translate(n.textContent)});
      document.title=translate(document.title);
      document.querySelectorAll('[aria-label],meta[name="description"]').forEach(el=>{for(const name of ['aria-label','content'])if(el.hasAttribute(name))el.setAttribute(name,translate(el.getAttribute(name)))});
    }
    const switcher=document.createElement('div');switcher.className='language-switch';switcher.setAttribute('role','group');switcher.setAttribute('aria-label',lang==='kk'?'Тілді таңдау':'Выбор языка');
    for(const [value,label] of [['ru','RU'],['kk','ҚАЗ']]){const a=document.createElement('a');const url=new URL(location.href);url.searchParams.set('lang',value);a.href=url.pathname+url.search+url.hash;a.textContent=label;a.lang=value;a.hreflang=value;a.classList.toggle('active',value===lang);a.addEventListener('click',e=>{e.preventDefault();url.hash=location.hash;location.href=url.pathname+url.search+url.hash});switcher.append(a)}
    document.querySelector('header').append(switcher);
    const script=document.createElement('script');script.src=lang==='kk'?'app.kk.js':'app.js';document.head.append(script);
  });
})();
