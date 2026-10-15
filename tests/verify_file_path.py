"""Verify that the published pathway contains every original cell and image."""
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_notebooks import clean_markdown,cleaner
catalog=json.loads((ROOT/'dist/file-course.json').read_text(encoding='utf-8'))
assert [x['id'] for x in catalog]==[f'{i:02d}' for i in range(1,8)]
total=0
for item in catalog:
    source=ROOT/'courses'/item['sourcePath']
    raw=source.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==item['sha256']
    assert (ROOT/'dist'/item['download']).read_bytes()==raw
    original=json.loads(raw)
    published=json.loads((ROOT/'dist/file-lessons'/f"{item['id']}.json").read_text(encoding='utf-8'))
    assert len(published['cells'])==len(original['cells'])==item['cellCount']
    for before,after in zip(original['cells'],published['cells']):
        assert before['cell_type']==after['type']
        if before['cell_type'] in ['code','raw']:
            assert after['source']==''.join(before['source'])
        for image in re.findall(r'src="(course-assets/[^"]+)"',after.get('html','')):
            assert (ROOT/'dist'/image).is_file()
        for output in after.get('outputs',[]):
            if output['type']=='image':assert (ROOT/'dist'/output['src']).is_file()
    for lang in ['ru','kk']:
        guide=item[lang]
        assert len(guide['goals'])>=3
        assert guide['intro'] and guide['task'] and guide['expected'] and guide['warning']
        assert len(guide['quiz']['options'])==3 and guide['quiz']['answer'] in range(3)
    total+=item['cellCount']
    print(f"PASS file lesson {item['id']}: all {item['cellCount']} source cells and download")
assert total==401
malicious='<script>window.pwned=1</script><img src="x" onerror="alert(1)"><a href="javascript:alert(1)">bad</a><iframe src="https://example.com"></iframe>'
for render in [cleaner.clean,clean_markdown]:
    sanitized=render(malicious)
    assert '<script' not in sanitized and 'onerror=' not in sanitized and 'javascript:' not in sanitized and '<iframe' not in sanitized
print('PASS notebook markup sanitization and original provenance')
