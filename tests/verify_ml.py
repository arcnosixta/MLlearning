"""Run every published ML lab from its download and compare with the browser plots."""

import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_ml import WEEKS, validate_lesson


def compare(actual, expected):
    if type(expected) in (float, int):
        assert math.isclose(actual, expected, rel_tol=1e-5, abs_tol=1e-6), (actual, expected)
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected):
            compare(left, right)
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key, value in expected.items():
            compare(actual[key], value)
    else:
        assert actual == expected, (actual, expected)


dist = ROOT / 'dist'
ml = dist / 'ml'
index = json.loads((ml / 'index.json').read_text(encoding='utf-8'))
assert [week['id'] for week in index['weeks']] == WEEKS
assert index['project']['id'] == 'project'
assert not any((dist / name).exists() for name in ('lessons.json', 'lessons.kk.json', 'file-course.json', 'examples', 'file-lessons', 'notebooks', 'lab.js', 'lab.kk.js'))
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONIOENCODING='utf-8')
topic_count = 0
for ident in [*WEEKS, 'project']:
    output = ml / ident
    expected = json.loads((output / 'results.json').read_text(encoding='utf-8'))
    lesson = json.loads((output / 'lesson.json').read_text(encoding='utf-8'))
    validate_lesson(lesson, expected, ident)
    topic_count += len(expected['topics'])
    assert lesson['ru']['title'] != lesson['kk']['title']
    with ZipFile(output / 'lab.zip') as archive, tempfile.TemporaryDirectory() as temporary:
        names = {'lab.py', 'results.json', 'requirements.txt', *lesson['assets']}
        assert set(archive.namelist()) == names
        for name in names - {'requirements.txt'}:
            assert archive.read(name) == (output / name).read_bytes(), (ident, name)
        archive.extractall(temporary)
        if 'extra.py' in names:
            compile(archive.read('extra.py'), 'extra.py', 'exec')
        run = subprocess.run([sys.executable, 'lab.py'], cwd=temporary, env=env, encoding='utf-8', capture_output=True, timeout=60, check=True)
        compare(json.loads(run.stdout), expected)
    print(f'PASS {ident}: {len(expected["topics"])} reproduced experiments', flush=True)
print(f'PASS 14 weeks plus capstone, {topic_count} bilingual topics and runnable downloads')
