"""Validate imported notebooks and their exact source digests, without executing cells."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'sources.json').read_text(encoding='utf-8'))
assert manifest['schema_version']==1
seen=set()
for item in manifest['items']:
    assert item['number'] not in seen
    seen.add(item['number'])
    path=(root/item['path']).resolve()
    assert path.is_relative_to(root) and path.suffix=='.ipynb'
    raw=path.read_bytes()
    assert len(raw)==item['bytes']
    assert hashlib.sha256(raw).hexdigest()==item['sha256']
    notebook=json.loads(raw)
    assert notebook['nbformat']==4 and len(notebook['cells'])==item['cells']
    for cell in notebook['cells']:
        assert cell['cell_type'] in ['code','markdown','raw']
        source=cell.get('source',[])
        assert isinstance(source,str) or (isinstance(source,list) and all(isinstance(s,str) for s in source))
    print(f"PASS imported notebook {item['number']:02d}: {item['cells']} cells, verified SHA-256")
assert len(list(root.rglob('*.ipynb')))==len(seen)
print(f'Verified {len(seen)} notebooks; no cells executed.')
