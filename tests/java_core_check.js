// Execute with Node; both modules are pure and also run in the browser.
const fs=require('node:fs');global.window=globalThis;
eval(fs.readFileSync('java/exam-core.js','utf8'));
eval(fs.readFileSync('java/terminal.js','utf8'));
const assert=require('node:assert/strict');
const weeks=JSON.parse(fs.readFileSync('dist/java-course.json','utf8'));
const exams=JSON.parse(fs.readFileSync('dist/java-exams.json','utf8'));
const all=weeks.flatMap(w=>w.questions);
for(const config of exams){
  for(const seed of [1,42,999,4294967295]){
    const ids=IMExam.select(weeks,config,seed);
    assert.equal(ids.length,config.count);assert.equal(new Set(ids).size,config.count);
    assert.deepEqual(ids,IMExam.select(weeks,config,seed));
    const selected=all.filter(q=>ids.includes(q.id));
    for(const n of config.weeks)assert(selected.some(q=>q.week===n));
    const run={questionIds:ids,answers:Object.fromEntries(selected.map(q=>[q.id,q.answer]))};
    assert.equal(IMExam.score(run,all).percent,100);
    run.answers={};assert.equal(IMExam.score(run,all).correct,0);
  }
}
assert(IMTerminal.check(' abstract  int area ( ) ; ',['abstract int area();']));
assert(!IMTerminal.check('Abstract int area();',['abstract int area();']));
assert(!IMTerminal.check('abstractintarea();',['abstract int area();']));
assert(!IMTerminal.check('javacMain.java',['javac Main.java']));
assert(!IMTerminal.check('<script>alert(1)</script>',['private']));
console.log('PASS exam coverage/reproducibility/scoring and terminal normalization');
