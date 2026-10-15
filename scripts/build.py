"""Build a portable static site, without a JavaScript toolchain."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
for name in ['index.html', 'styles.css', 'app.js', 'icon.svg', 'lab.js']:
    source = ROOT / name
    if source.exists():
        shutil.copy2(source, OUT / name)
lessons = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'lessons').glob('*.json'))]
(OUT / 'lessons.json').write_text(json.dumps(lessons, ensure_ascii=False), encoding='utf-8')
if (ROOT / 'examples').exists():
    shutil.copytree(ROOT / 'examples', OUT / 'examples', dirs_exist_ok=True)
print(f'Built {len(lessons)} lessons in {OUT}')
