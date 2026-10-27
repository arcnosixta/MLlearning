"""Verify complete playlist coverage, authored guides and isolated lab examples."""
from collections import Counter
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sysadmin/full'
playlist = json.loads((SOURCE / 'playlist.json').read_text(encoding='utf-8'))
definitions = json.loads((SOURCE / 'groups.json').read_text(encoding='utf-8'))
data = json.loads((ROOT / 'dist/sysadmin-full/catalog.json').read_text(encoding='utf-8'))
entries, groups = data['entries'], data['groups']
assert len(playlist['entries']) == len(entries) == playlist['videoCount'] == 106
assert len(definitions) == len(groups) == 35
assert [entry['index'] for entry in entries] == list(range(1, 107))
assert [entry['courseId'] for entry in entries] == [f'{number:03d}' for number in range(1, 107)]
assert [entry['id'] for entry in entries] == [entry['id'] for entry in playlist['entries']]
assert len({entry['id'] for entry in entries}) == 106
assert entries[0]['id'] == 'K8W4VUJQdX4' and entries[-1]['id'] == 'LvbX8c8awA4'
assert 'z9QXFXOI0f0' in {entry['id'] for entry in entries}
assert data['playlistId'] == playlist['playlistId'] == 'PLYl91BhaOf-kkXWweBzgOw555he6S7SUs'
assert sum(entry['durationSeconds'] for entry in entries) == data['totalDurationSeconds']
assert [group['id'] for group in groups] == [f'{number:02d}' for number in range(1, 36)]
assert Counter(video for group in groups for video in group['videoIds']) == Counter(entry['id'] for entry in entries)
group_by_id = {group['id']: group for group in groups}
for original, entry in zip(playlist['entries'], entries):
    assert all(entry[key] == value for key, value in original.items())
    assert re.fullmatch(r'[A-Za-z0-9_-]{11}', entry['id'])
    assert entry['url'] == 'https://www.youtube.com/watch?v=' + entry['id']
    assert entry['durationSeconds'] > 0 and entry['title']
    assert entry['id'] in group_by_id[entry['guideId']]['videoIds']
assert {group['id'] for group in groups} == {entry['guideId'] for entry in entries}

explanations = {'ru': set(), 'kk': set()}
bash = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' else 'bash'
with tempfile.TemporaryDirectory() as temporary:
    for group in groups:
        ident = group['id']
        folder = SOURCE / 'guides' / ident
        assert group['relatedWeeks'] and all(isinstance(n, int) and n in range(1, 14) for n in group['relatedWeeks'])
        assert group['code'] == (folder / 'lab.sh').read_text(encoding='utf-8')
        download = ROOT / 'dist' / group['download']
        assert download.is_file() and download.is_relative_to(ROOT / 'dist/sysadmin-full/labs')
        assert group['code'] == download.read_text(encoding='utf-8')
        assert group['output'] == (folder / 'output.txt').read_text(encoding='utf-8').strip()
        for lang, minimum in [('ru', 150), ('kk', 75)]:
            text = group[lang]
            html = text['html']
            assert text['title'] and text['description']
            assert len(re.sub('<[^>]*>', ' ', html).split()) >= minimum, (ident, lang)
            assert html.count('<h2>') >= 3, (ident, lang)
            assert html.count('<details>') == html.count('<summary>') == 3
            assert all(html.count('{{answer:' + str(n) + '}}') == 1 for n in range(1, 4))
            assert '{{example}}' not in html and '<script' not in html.lower() and '<iframe' not in html.lower()
            # Every topic must have its own authored explanation, beyond the example.
            raw = (folder / f'{lang}.md').read_text(encoding='utf-8')
            assert raw not in explanations[lang], (ident, lang)
            explanations[lang].add(raw)
        assert group['ru']['html'] != group['kk']['html']
        syntax = subprocess.run([bash, '-n', str(download)], capture_output=True, text=True, encoding='utf-8', timeout=30)
        assert syntax.returncode == 0, (ident, syntax.stderr)
        executed = subprocess.run([bash, str(download)], cwd=temporary, capture_output=True, text=True, encoding='utf-8', timeout=30,
                                  env=dict(os.environ, LC_ALL='C', LANG='C'))
        assert executed.returncode == 0, (ident, executed.stdout, executed.stderr)
        assert executed.stdout.strip() == group['output'], (ident, executed.stdout, group['output'])
        print('PASS sysadmin topic guide and lab', ident, flush=True)
assert set().union(*(set(group['relatedWeeks']) for group in groups)) == set(range(1, 14))
print('PASS all 106 original videos, 35 bilingual guides, 105 exercises and isolated Bash labs')
