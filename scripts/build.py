"""Build a portable static site, without a JavaScript toolchain."""
import json
import shutil
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
for name in ['index.html', 'styles.css', 'app.js', 'icon.svg', 'lab.js', 'locale.js', 'storage.js']:
    source = ROOT / name
    if source.exists():
        shutil.copy2(source, OUT / name)
app_source='\n'.join((ROOT/name).read_text(encoding='utf-8') for name in ['app.js','data-view.js','files-view.js'])
(OUT/'app.js').write_text(app_source,encoding='utf-8')
lessons = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'lessons').glob('*.json'))]
(OUT / 'lessons.json').write_text(json.dumps(lessons, ensure_ascii=False), encoding='utf-8')
if (ROOT / 'examples').exists():
    shutil.copytree(ROOT / 'examples', OUT / 'examples', dirs_exist_ok=True)
print(f'Built {len(lessons)} lessons in {OUT}')

# Generate localized assets from one application source, with longest-match,
# single-pass replacements: translated words are never translated a second time.
dictionary = json.loads((ROOT/'i18n/ui.kk.json').read_text(encoding='utf-8'))
pattern = re.compile('|'.join(re.escape(k) for k in sorted(dictionary,key=len,reverse=True)))
for name in ['app', 'lab']:
    text = app_source if name == 'app' else (ROOT/f'{name}.js').read_text(encoding='utf-8')
    text = pattern.sub(lambda match:dictionary[match[0]], text)
    if name == 'app':
        text = text.replace("fetch('lessons.json')", "fetch('lessons.kk.json')")
        text = text.replace("s.src='lab.js'", "s.src='lab.kk.js'")
        text = text.replace('href="examples/', 'href="examples/kk/')
    (OUT/f'{name}.kk.js').write_text(text,encoding='utf-8')
shutil.copy2(ROOT/'i18n/ui.kk.json', OUT/'ui.kk.json')
translations=json.loads((ROOT/'i18n/lessons.kk.json').read_text(encoding='utf-8'))
assert len(translations)==len(lessons)==24
localized=[]
(OUT/'examples/kk').mkdir(exist_ok=True)
code_words={'условные единицы':'шартты бірлік','Учебная модель с нулевым свободным членом':'Бос мүшесі нөлге тең оқу моделі','Цена для':'Баға, аудан','Нужен хотя бы один элемент':'Кемінде бір элемент қажет','футбол команда гол':'футбол команда гол','хоккей команда матч':'хоккей команда матч','спорт победа футбол':'спорт жеңіс футбол','код программа python':'код бағдарлама python','python данные код':'python деректер код','программа алгоритм данные':'бағдарлама алгоритм деректер','данные python':'деректер python'}
code_pattern=re.compile('|'.join(re.escape(k) for k in sorted(code_words,key=len,reverse=True)))
for original, translated in zip(lessons,translations):
    row={**original,**translated}
    assert set(translated)=={'title','intro','theory','insight','expected','task','hint','quiz'}
    row['code']=code_pattern.sub(lambda m:code_words[m[0]],original['code'])
    localized.append(row)
    (OUT/'examples/kk'/f"{row['id']}.py").write_text(row['code'],encoding='utf-8')
(OUT/'lessons.kk.json').write_text(json.dumps(localized,ensure_ascii=False),encoding='utf-8')
print('Built complete Kazakh interface, 24 lessons and localized examples')

from build_notebooks import build as build_notebooks
build_notebooks()
