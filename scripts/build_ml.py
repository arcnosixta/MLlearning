"""Validate and package the bilingual ML semester and its runnable labs."""

import json
import math
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('ru', 'kk')
WEEKS = [f'{number:02d}' for number in range(1, 15)]
OPTIONAL_ASSETS = ('data.csv', 'extra.py', 'extra-requirements.txt')
TOPIC_TEXT = ('title', 'example', 'task', 'hint', 'solution', 'xLabel', 'yLabel', 'question', 'feedback')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')


def text(value):
    return isinstance(value, str) and bool(value.strip())


def bilingual(value):
    return isinstance(value, dict) and set(value) == set(LANGUAGES) and all(map(text, value.values()))


def validate_lesson(lesson, results, ident):
    if lesson['id'] != ident or not lesson['sources'] or not all(map(text, lesson['sources'])):
        raise ValueError(f'ML {ident}: missing ID or source notes')
    topics = results['topics']
    if not 3 <= len(topics) <= 6:
        raise ValueError(f'ML {ident}: expected 3–6 topics')
    if any(type(n) is not int or not 1 <= n <= len(topics) for n in lesson.get('independentAxes', [])):
        raise ValueError(f'ML {ident}: invalid topic with independent axes')
    for lang in LANGUAGES:
        content = lesson[lang]
        if not all(text(content[key]) for key in ('title', 'intro', 'assignment')) or not content['goals'] or not all(map(text, content['goals'])):
            raise ValueError(f'ML {ident} {lang}: incomplete lesson overview')
        if len(content['topics']) != len(topics):
            raise ValueError(f'ML {ident} {lang}: topics and experiments differ')
        for topic in content['topics']:
            if not all(text(topic[key]) for key in TOPIC_TEXT) or len(topic['theory']) < 3 or not all(map(text, topic['theory'])):
                raise ValueError(f'ML {ident} {lang}: incomplete topic')
            if len(topic['choices']) != 3 or not all(map(text, topic['choices'])) or type(topic['answer']) is not int or topic['answer'] not in range(3):
                raise ValueError(f'ML {ident} {lang}: invalid review question')
    for cases in topics:
        if len(cases) != 3 or len({case['label']['ru'] for case in cases}) != 3 or len({case['label']['kk'] for case in cases}) != 3:
            raise ValueError(f'ML {ident}: each experiment needs three named conditions')
        for case in cases:
            if not bilingual(case['label']) or not bilingual(case['note']) or not case['series']:
                raise ValueError(f'ML {ident}: incomplete chart')
            for tick in case.get('xTicks', []):
                if not math.isfinite(tick['value']) or not bilingual(tick['label']):
                    raise ValueError(f'ML {ident}: invalid chart label')
            for series in case['series']:
                if not bilingual(series['label']) or series['kind'] not in ('line', 'bar', 'scatter') or not series['points']:
                    raise ValueError(f'ML {ident}: invalid chart series')
                if not all(len(pair) == 2 and all(type(n) in (int, float) and math.isfinite(n) for n in pair) for pair in series['points']):
                    raise ValueError(f'ML {ident}: invalid chart point')


def package(path, files):
    with ZipFile(path, 'w') as archive:
        for name, raw in files.items():
            archive.writestr(ZipInfo(name), raw, compress_type=ZIP_DEFLATED)


def build(out):
    source = ROOT / 'ml'
    target = out / 'ml'
    requirements = '\n'.join(line for line in (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines()
                             if line.partition('==')[0] in ('numpy', 'pandas', 'scikit-learn', 'joblib', 'matplotlib', 'seaborn')) + '\n'
    index = {'weeks': []}
    topic_count = 0
    for ident in [*WEEKS, 'project']:
        folder = source / ('project' if ident == 'project' else f'weeks/{ident}')
        lesson, results = read(folder / 'lesson.json'), read(folder / 'results.json')
        validate_lesson(lesson, results, ident)
        topic_count += len(results['topics'])
        dest = target / ident
        dest.mkdir(parents=True, exist_ok=True)
        lesson['assets'] = [name for name in OPTIONAL_ASSETS if (folder / name).is_file()]
        write(dest / 'lesson.json', lesson)
        write(dest / 'results.json', results)
        names = ['lab.py', *lesson['assets']]
        for name in names:
            shutil.copyfile(folder / name, dest / name)
        package(dest / 'lab.zip', {
            **{name: (folder / name).read_bytes() for name in names},
            'results.json': (dest / 'results.json').read_bytes(),
            'requirements.txt': requirements.encode(),
        })
        summary = {
            'id': ident,
            'title': {lang: lesson[lang]['title'] for lang in LANGUAGES},
            'topics': {lang: [topic['title'] for topic in lesson[lang]['topics']] for lang in LANGUAGES},
        }
        if ident == 'project':
            index['project'] = {**summary, 'intro': {lang: lesson[lang]['intro'] for lang in LANGUAGES}}
        else:
            index['weeks'].append(summary)
    write(target / 'index.json', index)
    shutil.copyfile(source / 'styles.css', out / 'ml.css')
    print(f'Built ML 3305: 14 weeks, capstone and {topic_count} bilingual experiments')
