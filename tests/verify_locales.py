"""Check locale coverage and execute every localized Python download."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ru=json.loads((ROOT/'dist/lessons.json').read_text(encoding='utf-8'))
kk=json.loads((ROOT/'dist/lessons.kk.json').read_text(encoding='utf-8'))
assert len(ru)==len(kk)==24
env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
with tempfile.TemporaryDirectory() as work:
    for original,translated in zip(ru,kk):
        assert original['id']==translated['id']
        for key in ['intro','theory','insight','expected','task','hint']:
            assert translated[key] and translated[key]!=original[key],(original['id'],key)
        assert translated['quiz']['answer']==original['quiz']['answer']
        source=ROOT/'dist/examples/kk'/f"{translated['id']}.py"
        assert source.read_text(encoding='utf-8')==translated['code']
        result=subprocess.run([sys.executable,str(source)],cwd=work,env=env,capture_output=True,timeout=90)
        assert result.returncode==0,(translated['id'],result.stderr)
        print('PASS Kazakh example',translated['id'],flush=True)
print('PASS complete translation coverage')
