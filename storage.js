/* Versioned browser-local learning records. No requests or user data upload. */
(()=>{
  const KEY='mllearning-data-v1',ids=new Set(Array.from({length:24},(_,i)=>String(i+1).padStart(2,'0')));
  const fileIds=new Set(['01','02','03','04','05','06','07']);
  const blankFiles=()=>({completed:[],answers:{},notes:{},lastLesson:null});
  const blank=()=>({version:1,updatedAt:new Date().toISOString(),completed:[],answers:{},notes:{},lastLesson:null,labs:{active:'regression'},language:'ru',files:blankFiles()});
  const plain=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
  const controls={regression:{weight:[-0.5,3],bias:[-3,7]},scaling:{'scale-mode':['raw','standard','minmax'],multiplier:[1,100]},knn:{k:[1,11],'query-x':[0,10],'query-y':[0,10]}};
  function validate(input){
    if(!plain(input)||input.version!==1||!Array.isArray(input.completed)||!plain(input.answers)||!plain(input.notes)||!plain(input.labs))throw new Error('Invalid backup');
    if(input.completed.some(id=>!ids.has(id))||!['ru','kk'].includes(input.language)||(input.lastLesson!==null&&!ids.has(input.lastLesson)))throw new Error('Invalid record');
    const out=blank();out.completed=[...new Set(input.completed)];out.lastLesson=input.lastLesson;out.language=input.language;
    for(const [id,value] of Object.entries(input.answers)){if(!ids.has(id)||!Number.isInteger(value)||value<0||value>2)throw new Error('Invalid answer');out.answers[id]=value}
    for(const [id,value] of Object.entries(input.notes)){if(!ids.has(id)||typeof value!=='string'||value.length>10000)throw new Error('Invalid note');out.notes[id]=value}
    if(!Object.hasOwn(controls,input.labs.active))throw new Error('Invalid experiment');out.labs.active=input.labs.active;
    for(const type of Object.keys(controls)){
      if(input.labs[type]===undefined)continue;
      if(!plain(input.labs[type]))throw new Error('Invalid controls');
      out.labs[type]={};
      for(const [name,value] of Object.entries(input.labs[type])){
        if(!Object.hasOwn(controls[type],name)||typeof value!=='string')throw new Error('Invalid control');
        const rule=controls[type][name];
        if(typeof rule[0]==='string'){if(!rule.includes(value))throw new Error('Invalid option')}
        else if(!value.trim()||!Number.isFinite(Number(value))||Number(value)<rule[0]||Number(value)>rule[1]||(name==='k'&&(!Number.isInteger(Number(value))||Number(value)%2!==1)))throw new Error('Invalid range');
        out.labs[type][name]=value;
      }
    }
    // Additive schema: old version-1 backups without a file pathway still load.
    if(input.files!==undefined){
      const f=input.files;
      if(!plain(f)||!Array.isArray(f.completed)||f.completed.some(id=>!fileIds.has(id))||!plain(f.answers)||!plain(f.notes)||(f.lastLesson!==null&&!fileIds.has(f.lastLesson)))throw new Error('Invalid file pathway');
      out.files.completed=[...new Set(f.completed)];out.files.lastLesson=f.lastLesson;
      for(const [id,value] of Object.entries(f.answers)){if(!fileIds.has(id)||!Number.isInteger(value)||value<0||value>2)throw new Error('Invalid file answer');out.files.answers[id]=value}
      for(const [id,value] of Object.entries(f.notes)){if(!fileIds.has(id)||typeof value!=='string'||value.length>10000)throw new Error('Invalid file note');out.files.notes[id]=value}
    }
    return out;
  }
  let state=blank(),persistent=true;
  try{
    const raw=localStorage.getItem(KEY);
    if(raw)state=validate(JSON.parse(raw));
    else{
      const legacy=JSON.parse(localStorage.getItem('mllearning-progress')||'[]');
      if(Array.isArray(legacy))state.completed=[...new Set(legacy.filter(id=>ids.has(id)))];
      state.language=localStorage.getItem('mllearning-language')==='kk'?'kk':'ru';
    }
  }catch{persistent=false}
  function save(next){state=validate(next);try{localStorage.setItem(KEY,JSON.stringify(state));persistent=true;return true}catch{persistent=false;return false}}
  function update(patch){return save({...state,...patch})}
  window.MLStore={
    get:()=>structuredClone(state),
    isPersistent:()=>persistent,
    update,
    answer:(id,value)=>update({answers:{...state.answers,[id]:value}}),
    note:(id,value)=>update({notes:{...state.notes,[id]:value}}),
    fileVisit:id=>update({files:{...state.files,lastLesson:id}}),
    fileNote:(id,value)=>update({files:{...state.files,notes:{...state.files.notes,[id]:value}}}),
    fileAnswer:(id,value)=>update({files:{...state.files,answers:{...state.files.answers,[id]:value}}}),
    fileComplete:id=>update({files:{...state.files,completed:[...new Set([...state.files.completed,id])]}}),
    export:()=>JSON.stringify(state,null,2),
    import:text=>save(validate(JSON.parse(text))),
    resetProgress:()=>update({completed:[]}),
    clear:()=>{state=blank();try{localStorage.removeItem(KEY);localStorage.removeItem('mllearning-progress');localStorage.removeItem('mllearning-language');persistent=true;return true}catch{persistent=false;return false}},
    bindLab:(el,type)=>{
      el._storageListeners?.abort();
      const controller=new AbortController();el._storageListeners=controller;
      const saved=state.labs[type]||{};
      for(const [id,value] of Object.entries(saved)){const control=el.querySelector('#'+id);if(control)control.value=value}
      if(Object.keys(saved).length){const input=el.querySelector('select,input');input?.dispatchEvent(new Event(input.tagName==='SELECT'?'change':'input',{bubbles:true}))}
      function record(){const values={};for(const control of el.querySelectorAll('input[id],select[id]'))values[control.id]=control.value;update({labs:{...state.labs,active:type,[type]:values}})}
      for(const event of ['input','change','click'])el.addEventListener(event,record,{signal:controller.signal});record();
    }
  };
})();
