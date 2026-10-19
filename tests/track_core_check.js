const fs=require('node:fs'),assert=require('node:assert/strict');
global.window=globalThis;
const saved=new Map();global.localStorage={getItem:k=>saved.get(k)||null,setItem:(k,v)=>saved.set(k,v),removeItem:k=>saved.delete(k)};
for(const file of ['track-config.js','java/exam-core.js','storage.js'])eval(fs.readFileSync(file,'utf8'));
const tracks=JSON.parse(fs.readFileSync('dist/tracks.json','utf8'));
for(const track of tracks){
  const all=track.lessons.flatMap(l=>l.questions);
  assert.equal(track.lessons.length,13);assert.equal(all.length,65);
  for(const [kind,config] of Object.entries(IMTrackConfig.controls)){
    for(const seed of [0,42,4294967295]){
      const ids=IMExam.select(track.lessons,config,seed);
      assert.equal(ids.length,config.count);assert.equal(new Set(ids).size,config.count);
      assert.deepEqual(ids,IMExam.select(track.lessons,config,seed));
      const selected=all.filter(q=>ids.includes(q.id));
      assert(selected.every(q=>config.weeks.includes(q.week)));
      for(const week of config.weeks)assert(selected.some(q=>q.week===week));
      const run={id:'test-'+seed.toString(36),kind,seed,startedAt:1000,deadline:1000+config.minutes*60000,submittedAt:null,questionIds:ids,answers:Object.fromEntries(selected.map(q=>[q.id,q.answer]))};
      assert(MLStore.trackUpdate(track.id,{active:run}));assert.equal(IMExam.score(run,all).percent,100);
      // Reopening storage must preserve old and new control formats.
      eval(fs.readFileSync('storage.js','utf8'));assert.deepEqual(MLStore.get().tracks[track.id].active,run);
      const before=MLStore.export();
      for(const mutate of [r=>r.deadline++,r=>r.questionIds[0]=track.id+'-14-q1',r=>r.questionIds[1]=r.questionIds[0],r=>r.questionIds[0]='foreign-01-q1',r=>r.answers[r.questionIds[0]]=3]){
        const invalid=structuredClone(run);mutate(invalid);assert.throws(()=>MLStore.trackUpdate(track.id,{active:invalid}));assert.equal(MLStore.export(),before);
      }
      // The other RK's weeks must be rejected even though question IDs exist.
      if(kind==='rk1'||kind==='rk2'||kind==='final'){
        const wrong=structuredClone(run);wrong.questionIds[0]=track.id+(kind==='rk2'?'-01-q1':'-13-q1');
        assert.throws(()=>MLStore.trackUpdate(track.id,{active:wrong}));
      }
      run.submittedAt=run.deadline;assert(MLStore.trackUpdate(track.id,{active:null,history:[run]}));
      MLStore.import(MLStore.export());assert.equal(MLStore.get().tracks[track.id].history[0].kind,kind);
      assert.equal(IMExam.score({...run,answers:{}},all).correct,0);
    }
  }
  MLStore.trackUpdate(track.id,{completed:['01','13'],notes:{'01':'old','13':'new'},quiz:{[track.id+'-13-q5']:2}});
  MLStore.import(MLStore.export());assert.equal(MLStore.get().tracks[track.id].notes['01'],'old');
}
const old=MLStore.get();delete old.tracks;MLStore.import(JSON.stringify(old));assert.equal(MLStore.get().tracks.go.completed.length,0);
console.log('PASS all course RK/session coverage, scoring, legacy attempts, schema rejection and reload persistence');
