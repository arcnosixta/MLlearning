'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const scope = vm.createContext({
  window: {ML_LOCALE: 'ru'}, Intl,
  mlText: value => value.ru,
  jt: ru => ru,
  escapeHTML: value => String(value),
});
vm.runInContext(fs.readFileSync('ml/chart.js', 'utf8'), scope);
const bilingual = value => ({ru: value, kk: value});
const current = {label: bilingual('neighbors'), series: [{
  label: bilingual('group'), kind: 'scatter', points: [[0, 0], [1, 0], [0, 1]],
}]};
for (const width of [250, 590]) {
  const topic = {title: 't-SNE', xLabel: 't-SNE 1', yLabel: 't-SNE 2', equalAspect: true};
  scope.args = [[current], current, topic, true, width];
  const svg = vm.runInContext('mlPlot(...args)', scope);
  const points = [...svg.matchAll(/<circle cx="([^"]+)" cy="([^"]+)"/g)]
    .map(match => [Number(match[1]), Number(match[2])]);
  assert.equal(points.length, 3);
  const dx = Math.abs(points[1][0] - points[0][0]);
  const dy = Math.abs(points[2][1] - points[0][1]);
  assert.ok(dx > 0 && Math.abs(dx - dy) < 1e-9, `Same data distance must render equally at ${width}px`);
  assert.ok(points.every(point => point.every(Number.isFinite)));
  const normal = {...topic}; delete normal.equalAspect;
  scope.args = [[current], current, normal, true, width];
  const prior = vm.runInContext('mlPlot(...args)', scope);
  scope.args[2] = {...normal, equalAspect: false};
  assert.equal(vm.runInContext('mlPlot(...args)', scope), prior, 'Other charts retain their existing geometry');
}
console.log('PASS equal t-SNE axis scales at mobile/desktop sizes; other chart geometry preserved');
