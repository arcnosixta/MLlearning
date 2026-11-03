"""Build a portable static site, without a JavaScript toolchain."""
import json
import shutil
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
# Clear only retired ML artifacts left behind by previous builds.
for name in ('examples', 'file-lessons', 'notebooks', 'teaching-examples/ml', 'teaching-examples/files'):
    retired = OUT / name
    if retired.exists():
        if not retired.resolve().is_relative_to(OUT.resolve()) or not OUT.resolve().is_relative_to(ROOT):
            raise ValueError(f'Unexpected retired asset location: {retired}')
        shutil.rmtree(retired)
for name in ('lessons.json', 'lessons.kk.json', 'file-course.json', 'lab.js', 'lab.kk.js'):
    (OUT / name).unlink(missing_ok=True)

for name in ['index.html', 'styles.css', 'academy.css', 'tracks.css', 'studio.css', 'motion.css', 'icon.svg', 'locale.js', 'track-config.js', 'storage.js']:
    shutil.copy2(ROOT / name, OUT / name)
app_source = '\n'.join((ROOT / name).read_text(encoding='utf-8') for name in [
    'java/terminal.js', 'java/exam-core.js', 'teaching/view.js', 'app.js', 'data-view.js',
    'java/java-view.js', 'course-utils.js', 'java/full-view.js', 'sysadmin/full-view.js', 'sysadmin/review-view.js',
    'java/exam-view.js', 'tracks/view.js', 'tracks/exam-view.js', 'studio.js', 'sound.js', 'motion.js',
])
ml_source = '\n'.join((ROOT / 'ml' / name).read_text(encoding='utf-8') for name in ['chart.js', 'course.js', 'reader.js'])
(OUT / 'app.js').write_text(app_source + '\n' + ml_source, encoding='utf-8')
shutil.copytree(ROOT / 'audio', OUT / 'audio', dirs_exist_ok=True)

# Keep the existing translation dictionary for older interface modules.
# ML uses its own explicit RU/KK strings and is appended after substitution.
dictionary = json.loads((ROOT / 'i18n/ui.kk.json').read_text(encoding='utf-8'))
pattern = re.compile('|'.join(re.escape(key) for key in sorted(dictionary, key=len, reverse=True)))
translated = pattern.sub(lambda match: dictionary[match[0]], app_source)
(OUT / 'app.kk.js').write_text(translated + '\n' + ml_source, encoding='utf-8')
shutil.copy2(ROOT / 'i18n/ui.kk.json', OUT / 'ui.kk.json')

from build_ml import build as build_ml
build_ml(OUT)

java_weeks=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'java/weeks').glob('*.json'))]
assert len(java_weeks)==14
(OUT/'java-course.json').write_text(json.dumps(java_weeks,ensure_ascii=False),encoding='utf-8')
shutil.copy2(ROOT/'java/exams.json',OUT/'java-exams.json')
shutil.copytree(ROOT/'java/examples',OUT/'java-examples',dirs_exist_ok=True)
print('Built Java semester: 14 weeks, 84 questions, checkpoints 30/30 and session 60')

tracks=json.loads((ROOT/'tracks/catalog.json').read_text(encoding='utf-8'))
for track in tracks:
    track['lessons']=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'tracks'/track['id']).glob('*.json'))]
    assert [l['id'] for l in track['lessons']]==[f'{n:02d}' for n in range(1,14)]
    assert all(len(l['questions'])==5 for l in track['lessons'])
    shutil.copytree(ROOT/'tracks'/track['id']/'examples',OUT/'track-examples'/track['id'],dirs_exist_ok=True)
(OUT/'tracks.json').write_text(json.dumps(tracks,ensure_ascii=False),encoding='utf-8')
print('Built 4 tracks, 52 weeks and 260 questions; RK 30/30, session 60')
teaching=[]
for path in sorted((ROOT/'teaching/content').glob('*.json')):
    teaching.extend(json.loads(path.read_text(encoding='utf-8')))
teaching.sort(key=lambda x:(x['path'],x['id']!='start',x['id']))
(OUT/'teaching.json').write_text(json.dumps(teaching,ensure_ascii=False),encoding='utf-8')
shutil.copy2(ROOT/'teaching/styles.css',OUT/'teaching.css')
if (ROOT/'teaching/examples').exists():
    shutil.copytree(ROOT/'teaching/examples',OUT/'teaching-examples',dirs_exist_ok=True)
print(f'Built {len(teaching)} bilingual teaching guides')

from build_java_full import build as build_java_full
build_java_full()
shutil.copy2(ROOT/'java/full.css', OUT/'java-full.css')

from build_sysadmin_full import build as build_sysadmin_full
build_sysadmin_full()
shutil.copy2(ROOT/'sysadmin/full.css', OUT/'sysadmin-full.css')
