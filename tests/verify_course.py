"""Execute every downloadable example and check the published course contract."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lessons = json.loads((ROOT/'dist/lessons.json').read_text(encoding='utf-8'))
assert len(lessons) == 24
assert [l['id'] for l in lessons] == [f'{i:02d}' for i in range(1,25)]
assert {l['group'] for l in lessons} == set(range(6))
env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONIOENCODING='utf-8')
with tempfile.TemporaryDirectory() as work:
    for lesson in lessons:
        assert len(lesson['theory']) >= 3
        assert 0 <= lesson['quiz']['answer'] < len(lesson['quiz']['options'])
        example = ROOT/'dist/examples'/f"{lesson['id']}.py"
        assert example.read_text(encoding='utf-8') == lesson['code']
        result = subprocess.run([sys.executable,str(example)], cwd=work, env=env, capture_output=True, text=True, encoding='utf-8', timeout=90)
        assert result.returncode == 0, f"Lesson {lesson['id']}: {result.stderr}"
        assert result.stdout.strip(), lesson['id']
        print(f"PASS example {lesson['id']}", flush=True)
    assert (Path(work)/'model.joblib').exists()
print('All 24 examples and curriculum checks passed.')
