"""Run every published ML lab from its download and compare with the browser plots."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_ml import WEEKS, validate_lesson
from ml_results_check import compare_ml_results


dist = ROOT / 'dist'
ml = dist / 'ml'
index = json.loads((ml / 'index.json').read_text(encoding='utf-8'))
assert [week['id'] for week in index['weeks']] == WEEKS
assert index['project']['id'] == 'project'
assert not any((dist / name).exists() for name in ('lessons.json', 'lessons.kk.json', 'file-course.json', 'examples', 'file-lessons', 'notebooks', 'lab.js', 'lab.kk.js'))
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONIOENCODING='utf-8')
SIMPLE_CHECK = '''
import io
import runpy
runpy.run_path("lab.py", run_name="__main__")
import matplotlib.pyplot as plt
assert plt.get_fignums(), "The example must produce a chart"
for number in plt.get_fignums():
    figure = plt.figure(number)
    assert any(axis.get_title() or axis.get_xlabel() for axis in figure.axes), "Label the chart"
    png = io.BytesIO()
    figure.savefig(png, format="png")
    assert png.getvalue().startswith(bytes([137, 80, 78, 71, 13, 10, 26, 10]))
'''
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
        script = 'experiments.py' if 'experiments.py' in names else 'lab.py'
        run = subprocess.run([sys.executable, script], cwd=temporary, env=env, encoding='utf-8', capture_output=True, timeout=60, check=True)
        compare_ml_results(json.loads(run.stdout), expected, ident)
        if script == 'experiments.py':
            outputs = []
            for language in ('ru', 'kk'):
                simple = subprocess.run([sys.executable, '-c', SIMPLE_CHECK], cwd=temporary,
                    env=dict(env, MPLBACKEND='Agg', IMLEARNING_LANG=language), encoding='utf-8',
                    capture_output=True, timeout=60, check=True)
                assert 0 < len(simple.stdout.strip()) < 5000, (ident, language, simple.stdout)
                assert '"topics"' not in simple.stdout and '\\u04' not in simple.stdout, (ident, language)
                outputs.append(simple.stdout)
            assert outputs[0] != outputs[1], (ident, 'Output must follow selected language')
    print(f'PASS {ident}: {len(expected["topics"])} reproduced experiments', flush=True)
print(f'PASS 14 weeks plus capstone, {topic_count} bilingual topics and runnable downloads')
