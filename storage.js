/* Versioned browser-local learning records. No requests or user data upload. */
(()=>{
  const KEY='mllearning-data-v1',ids=new Set(Array.from({length:24},(_,i)=>String(i+1).padStart(2,'0')));
  const fileIds=new Set(['01','02','03','04','05','06','07']);
  const blankFiles=()=>({completed:[],answers:{},notes:{},lastLesson:null});
  const javaIds=new Set(Array.from({length:14},(_,i)=>String(i+1).padStart(2,'0')));
  const questionId=id=>typeof id==='string'&&/^j(0[1-9]|1[0-4])-[ct][1-3]$/.test(id);
  const blankJava=()=>({completed:[],notes:{},quiz:{},terminal:[],lastWeek:null,active:null,history:[]});
  const trackIds=['go','onec','java-advanced','sysadmin'];
  const trackLessons=new Set(window.IMTrackConfig.lessonIds);
  const blankTrack=()=>({completed:[],notes:{},quiz:{},terminal:[],lastLesson:null,active:null,history:[]});
  const blank=()=>({version:1,updatedAt:new Date().toISOString(),completed:[],answers:{},notes:{},lastLesson:null,labs:{active:'regression'},language:'ru',files:blankFiles(),java:blankJava(),tracks:Object.fromEntries(trackIds.map(id=>[id,blankTrack()])),learning:{completed:[],practice:{}}});
  const plain=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
  const controls={regression:{weight:[-0.5,3],bias:[-3,7]},scaling:{'scale-mode':['raw','standard','minmax'],multiplier:[1,100]},knn:{k:[1,11],'query-x':[0,10],'query-y':[0,10]}};
  function validateRun(run,finished){
    if(!plain(run)||!['rk1','rk2','session'].includes(run.type)||typeof run.id!=='string'||!/^[a-z0-9]+-[a-z0-9]+$/.test(run.id)||run.id.length>80||!Number.isInteger(run.seed)||run.seed<0||run.seed>4294967295)throw new Error('Invalid exam');
    const size=run.type==='session'?60:30,duration=(run.type==='session'?90:45)*60000;
    if(!Array.isArray(run.questionIds)||run.questionIds.length!==size||new Set(run.questionIds).size!==size||run.questionIds.some(id=>!questionId(id)))throw new Error('Invalid question set');
    if(run.questionIds.some(id=>{const n=Number(id.slice(1,3));return run.type==='rk1'?n>7:run.type==='rk2'?n<8:false}))throw new Error('Wrong exam topic');
    if(!Number.isSafeInteger(run.startedAt)||run.startedAt<0||run.deadline!==run.startedAt+duration||!plain(run.answers))throw new Error('Invalid exam time');
    if(finished?(!Number.isSafeInteger(run.submittedAt)||run.submittedAt<run.startedAt):run.submittedAt!==null)throw new Error('Invalid submission');
    const answers={};for(const [id,value] of Object.entries(run.answers)){if(!run.questionIds.includes(id)||!Number.isInteger(value)||value<0||value>2)throw new Error('Invalid exam answer');answers[id]=value}
    return {id:run.id,type:run.type,seed:run.seed,startedAt:run.startedAt,deadline:run.deadline,submittedAt:run.submittedAt,questionIds:[...run.questionIds],answers};
  }
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
    if(input.java!==undefined){
      const j=input.java;
      if(!plain(j)||!Array.isArray(j.completed)||j.completed.some(id=>!javaIds.has(id))||!Array.isArray(j.terminal)||j.terminal.some(id=>!javaIds.has(id))||!plain(j.notes)||!plain(j.quiz)||(j.lastWeek!==null&&!javaIds.has(j.lastWeek))||!Array.isArray(j.history)||j.history.length>10)throw new Error('Invalid Java records');
      out.java.completed=[...new Set(j.completed)];out.java.terminal=[...new Set(j.terminal)];out.java.lastWeek=j.lastWeek;
      for(const [id,value] of Object.entries(j.notes)){if(!javaIds.has(id)||typeof value!=='string'||value.length>10000)throw new Error('Invalid Java note');out.java.notes[id]=value}
      for(const [id,value] of Object.entries(j.quiz)){if(!questionId(id)||!Number.isInteger(value)||value<0||value>2)throw new Error('Invalid Java answer');out.java.quiz[id]=value}
      out.java.active=j.active===null?null:validateRun(j.active,false);out.java.history=j.history.map(run=>validateRun(run,true));
      if(new Set(out.java.history.map(r=>r.id)).size!==out.java.history.length)throw new Error('Duplicate attempt');
    }
    if(input.tracks!==undefined){
      if(!plain(input.tracks)||Object.keys(input.tracks).some(id=>!trackIds.includes(id)))throw new Error('Invalid tracks');
      for(const course of trackIds){
        if(input.tracks[course]===undefined)continue;
        const t=input.tracks[course],qvalid=id=>typeof id==='string'&&new RegExp('^'+course+'-(0[1-9]|1[0-3])-q[1-5]$').test(id);
        if(!plain(t)||!Array.isArray(t.completed)||t.completed.some(id=>!trackLessons.has(id))||!Array.isArray(t.terminal)||t.terminal.some(id=>!trackLessons.has(id))||!plain(t.notes)||!plain(t.quiz)||(t.lastLesson!==null&&!trackLessons.has(t.lastLesson))||!Array.isArray(t.history)||t.history.length>10)throw new Error('Invalid track records');
        const record=blankTrack();record.completed=[...new Set(t.completed)];record.terminal=[...new Set(t.terminal)];record.lastLesson=t.lastLesson;
        for(const [id,value] of Object.entries(t.notes)){if(!trackLessons.has(id)||typeof value!=='string'||value.length>10000)throw new Error('Invalid track note');record.notes[id]=value}
        for(const [id,value] of Object.entries(t.quiz)){if(!qvalid(id)||!Number.isInteger(value)||value<0||value>2)throw new Error('Invalid track answer');record.quiz[id]=value}
        function attempt(run,finished){
          const config=plain(run)&&Object.hasOwn(window.IMTrackConfig.controls,run.kind)?window.IMTrackConfig.controls[run.kind]:null;
          if(!config||typeof run.id!=='string'||!/^[a-z0-9]+-[a-z0-9]+$/.test(run.id)||run.id.length>80||!Number.isInteger(run.seed)||run.seed<0||run.seed>4294967295||!Array.isArray(run.questionIds)||run.questionIds.length!==config.count||new Set(run.questionIds).size!==run.questionIds.length||run.questionIds.some(id=>!qvalid(id)||!config.weeks.includes(Number(id.slice(course.length+1,course.length+3)))))throw new Error('Invalid track exam');
          if(!Number.isSafeInteger(run.startedAt)||run.startedAt<0||run.deadline!==run.startedAt+config.minutes*60000||!plain(run.answers)||(finished?(!Number.isSafeInteger(run.submittedAt)||run.submittedAt<run.startedAt):run.submittedAt!==null))throw new Error('Invalid track exam time');
          const answers={};for(const [id,value] of Object.entries(run.answers)){if(!run.questionIds.includes(id)||!Number.isInteger(value)||value<0||value>2)throw new Error('Invalid track exam answer');answers[id]=value}
          return {id:run.id,kind:run.kind,seed:run.seed,startedAt:run.startedAt,deadline:run.deadline,submittedAt:run.submittedAt,questionIds:[...run.questionIds],answers};
        }
        record.active=t.active===null?null:attempt(t.active,false);record.history=t.history.map(run=>attempt(run,true));if(new Set(record.history.map(r=>r.id)).size!==record.history.length)throw new Error('Duplicate track attempt');out.tracks[course]=record;
      }
    }
    if(input.learning!==undefined){
      const l=input.learning,limits={ml:24,files:7,java:14,'java-full':26,'sysadmin-full':106,'sysadmin-practice':35,go:13,onec:13,'java-advanced':13,sysadmin:13};
      const keyValid=key=>{if(typeof key!=='string')return false;const [path,id,...rest]=key.split('/');return rest.length===0&&Object.hasOwn(limits,path)&&(path==='sysadmin-full'?(/^\d{3}$/.test(id)&&Number(id)>=1&&Number(id)<=limits[path]):((id==='start'&&path!=='sysadmin-practice')||(/^\d{2}$/.test(id)&&Number(id)>=1&&Number(id)<=limits[path])))};
      if(!plain(l)||!Array.isArray(l.completed)||l.completed.some(k=>!keyValid(k))||!plain(l.practice))throw new Error('Invalid teaching records');
      out.learning.completed=[...new Set(l.completed)];
      for(const [key,value] of Object.entries(l.practice)){const parts=key.split('/'),number=parts.pop();if(!(['java-full','sysadmin-full'].includes(parts[0])?['1','2','3']:['1','2']).includes(number)||!keyValid(parts.join('/'))||typeof value!=='string'||value.length>10000)throw new Error('Invalid practice record');out.learning.practice[key]=value}
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
    javaUpdate:patch=>update({java:{...state.java,...patch}}),
    trackUpdate:(course,patch)=>{if(!trackIds.includes(course))throw new Error('Unknown track');return update({tracks:{...state.tracks,[course]:{...state.tracks[course],...patch}}})},
    learningUpdate:patch=>update({learning:{...state.learning,...patch}}),
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
