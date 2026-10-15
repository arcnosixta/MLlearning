/* Pure exam rules: balanced topic selection, unbiased seeded shuffling, scoring. */
(()=>{
  function shuffle(values,seed){const out=[...values];let state=seed>>>0;const next=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296};for(let i=out.length-1;i>0;i--){const j=Math.floor(next()*(i+1));[out[i],out[j]]=[out[j],out[i]]}return out}
  function select(weeks,config,seed){
    const pool=config.weeks.map(n=>weeks.find(w=>w.week===n));
    if(pool.some(w=>!w)||config.count>pool.reduce((n,w)=>n+w.questions.length,0))throw new Error('Exam bank incomplete');
    const chosen=[],groups=pool.map((w,i)=>shuffle(w.questions,seed+i*13));
    for(let index=0;chosen.length<config.count;index++)for(const group of groups){if(group[index]&&chosen.length<config.count)chosen.push(group[index].id)}
    return shuffle(chosen,seed+7);
  }
  function score(run,questions){const byId=new Map(questions.map(q=>[q.id,q]));let correct=0;const wrong=[],topics={};for(const id of run.questionIds){const q=byId.get(id);if(!q)throw new Error('Unknown question');const ok=run.answers[id]===q.answer;if(ok)correct++;else wrong.push(id);const topic=topics[q.week]||(topics[q.week]={correct:0,total:0});topic.total++;if(ok)topic.correct++}return {correct,total:run.questionIds.length,percent:Math.round(correct/run.questionIds.length*100),wrong,topics}}
  window.IMExam={shuffle,select,score};
})();
