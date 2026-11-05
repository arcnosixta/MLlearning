'use strict';

// Run with node tests/ml_python_protocol_check.js. No Python download is needed.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const context = vm.createContext({
  TextDecoder,
  self: {addEventListener() {}, postMessage() {}},
});
for (const file of ['ml/python-worker.js', 'ml/python-view.js']) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, {filename: file});
}
const extract = context.takeExperiment;
const acceptedByWorker = context.validExperiment;
const acceptedByView = value => Boolean(context.mlPythonChartTopics(value, value?.topics?.length));
const label = (ru = 'Наблюдения', kk = 'Бақылаулар') => ({ru, kk});
const experiment = () => ({topics: [[{
  label: label('Первый опыт', 'Бірінші тәжірибе'),
  note: label('Сравни точки с прямой.', 'Нүктелерді түзумен салыстыр.'),
  series: [{label: label(), kind: 'scatter', points: [[1, 2], [2, 4]]}],
}]]});
const clone = value => structuredClone(value);
let checks = 0;

function checkExtraction(name, text, expectedText, expectedExperiment, count = 1, truncated = false) {
  const capture = {text, truncated};
  const actual = extract(capture, count);
  assert.equal(capture.text, expectedText, `${name}: user output`);
  assert.equal(JSON.stringify(actual ?? null), JSON.stringify(expectedExperiment), `${name}: chart data`);
  checks++;
}

const chart = experiment();
const json = JSON.stringify(chart);
checkExtraction('protocol only', json + '\n', '', chart);
checkExtraction('ordinary prints before and after', `Начало\n${json}\nГотово\n`, 'Начало\nГотово\n', chart);
checkExtraction('indented protocol and CRLF', `before\r\n  ${json}\r\nafter\r\n`, 'before\r\nafter\r\n', chart);
checkExtraction('pretty printed protocol', `before\n${JSON.stringify(chart, null, 2)}\nafter`, 'before\nafter', chart);

const quoted = experiment();
quoted.topics[0][0].note = label('Скобки { и }, кавычка " и слеш \\.', 'Жолда { және } таңбалары бар.');
checkExtraction('braces and escaped quotes in labels', `${JSON.stringify(quoted)}\n`, '', quoted);
const escapedUnicode = json.replace(/[^\x00-\x7f]/g, char => '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0'));
checkExtraction('escaped Unicode from legacy labs', escapedUnicode + '\n', '', chart);

const changed = experiment();
changed.topics[0][0].series[0].points[1][1] = 8;
checkExtraction('latest complete protocol wins', `one\n${json}\ntwo\n${JSON.stringify(changed)}\nthree`, 'one\ntwo\nthree', changed);
checkExtraction('ordinary JSON preserved beside protocol', `{"result":42}\n${json}\n{"topics":[]}\n`, '{"result":42}\n{"topics":[]}\n', chart);
checkExtraction('ordinary JSON', '{"result":42}\n', '{"result":42}\n', null);
checkExtraction('malformed JSON', '{"topics": invalid}\n', '{"topics": invalid}\n', null);
checkExtraction('unfinished protocol', json.slice(0, -2), json.slice(0, -2), null);
checkExtraction('truncated capture preserved', json, json, null, 1, true);
checkExtraction('wrong lesson topic count', json + '\n', json + '\n', null, 2);
const invalid = experiment();
invalid.topics[0][0].series[0].points[0][1] = 'two';
checkExtraction('invalid chart schema preserved', JSON.stringify(invalid), JSON.stringify(invalid), null);

function checkValidators(name, value, expected) {
  assert.equal(Boolean(acceptedByWorker(value)), expected, `${name}: worker`);
  assert.equal(acceptedByView(value), expected, `${name}: view`);
  checks++;
}
function boundary(name, mutate, expected) {
  const value = experiment();
  mutate(value, value.topics[0][0]);
  checkValidators(name, value, expected);
}

checkValidators('small bilingual chart', experiment(), true);
checkValidators('null input', null, false);
boundary('six topics', value => {value.topics = Array.from({length: 6}, () => clone(value.topics[0]));}, true);
boundary('seven topics', value => {value.topics = Array.from({length: 7}, () => clone(value.topics[0]));}, false);
boundary('six conditions', (value, item) => {value.topics[0] = Array.from({length: 6}, () => clone(item));}, true);
boundary('seven conditions', (value, item) => {value.topics[0] = Array.from({length: 7}, () => clone(item));}, false);
boundary('sixteen series', (_, item) => {item.series = Array.from({length: 16}, () => clone(item.series[0]));}, true);
boundary('seventeen series', (_, item) => {item.series = Array.from({length: 17}, () => clone(item.series[0]));}, false);
boundary('thousand points', (_, item) => {item.series[0].points = Array.from({length: 1000}, (_, i) => [i, i]);}, true);
boundary('over point limit', (_, item) => {item.series[0].points = Array.from({length: 1001}, (_, i) => [i, i]);}, false);
boundary('longest label', (_, item) => {item.label.ru = 'x'.repeat(1200);}, true);
boundary('over label limit', (_, item) => {item.label.ru = 'x'.repeat(1201);}, false);
boundary('missing Kazakh translation', (_, item) => {delete item.note.kk;}, false);
boundary('empty translation', (_, item) => {item.note.kk = '';}, false);
boundary('numeric coordinate limit', (_, item) => {item.series[0].points[0][0] = 1e100;}, true);
boundary('coordinate over limit', (_, item) => {item.series[0].points[0][0] = 1e101;}, false);
boundary('nonfinite coordinate', (_, item) => {item.series[0].points[0][0] = Infinity;}, false);
boundary('invalid plot kind', (_, item) => {item.series[0].kind = 'script';}, false);
boundary('32 categorical ticks', (_, item) => {item.xTicks = Array.from({length: 32}, (_, i) => ({value: i, label: label()}));}, true);
boundary('33 categorical ticks', (_, item) => {item.xTicks = Array.from({length: 33}, (_, i) => ({value: i, label: label()}));}, false);
boundary('tick coordinate limit', (_, item) => {item.xTicks = [{value: 1e100, label: label()}];}, true);
boundary('tick coordinate over limit', (_, item) => {item.xTicks = [{value: 1e101, label: label()}];}, false);

console.log(`PASS ${checks} Python chart protocol extraction and worker/view schema checks`);
