"""Build the verified playlist index and authored bilingual topic guides.

The source videos remain on YouTube. The reader clearly distinguishes these
original videos from the site's own explanations and laboratory exercises.
"""
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

import bleach
import markdown

ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')


def build():
    source = ROOT / 'sysadmin/full'
    if not (source / 'playlist.json').exists() or not (source / 'groups.json').exists():
        print('Full sysadmin playlist sources are not ready yet')
        return
    playlist = json.loads((source / 'playlist.json').read_text(encoding='utf-8'))
    definitions = json.loads((source / 'groups.json').read_text(encoding='utf-8'))
    out = ROOT / 'dist/sysadmin-full'
    out.mkdir(parents=True, exist_ok=True)
    cleaner = bleach.Cleaner(
        tags={'p', 'h2', 'h3', 'h4', 'pre', 'code', 'ul', 'ol', 'li', 'strong', 'em',
              'blockquote', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'details', 'summary'},
        attributes={'a': ['href', 'title']}, protocols={'https', 'http'}, strip=True)
    groups = []
    video_groups = {}
    for definition in definitions:
        ident = definition['id']
        assert re.fullmatch(r'\d{2}', ident), ident
        folder = source / 'guides' / ident
        if not folder.exists():
            continue  # Allows concurrent authorship; the verifier enforces final coverage.
        code = (folder / 'lab.sh').read_text(encoding='utf-8')
        output = (folder / 'output.txt').read_text(encoding='utf-8').strip()
        download = f'sysadmin-full/labs/{ident}/lab.sh'
        item = {**definition, 'code': code, 'output': output, 'download': download}
        for lang in ['ru', 'kk']:
            raw = (folder / f'{lang}.md').read_text(encoding='utf-8')
            title, body = raw.split('\n', 1)
            assert title.startswith('# '), (ident, lang)
            assert body.count('{{example}}') == 1, (ident, lang)
            assert all(body.count('{{answer:' + str(n) + '}}') == 1 for n in range(1, 4)), (ident, lang)
            label = 'Ожидаемый вывод' if lang == 'ru' else 'Күтілетін нәтиже'
            example = '\n```bash\n' + code.rstrip() + '\n```\n\n**' + label + ':**\n\n```text\n' + output + '\n```\n'
            body = body.replace('{{example}}', example)
            rendered = cleaner.clean(markdown.markdown(body, extensions=['fenced_code', 'tables', 'sane_lists']))
            item[lang] = {'title': title[2:].strip(), 'html': rendered,
                          'description': re.sub(r'[*`]', '', body.strip().split('\n')[0])}
        target = out / 'labs' / ident
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(folder / 'lab.sh', target / 'lab.sh')
        for video in definition['videoIds']:
            assert VIDEO_ID.fullmatch(video), video
            assert video not in video_groups, ('Video assigned twice', video)
            video_groups[video] = ident
        groups.append(item)
    entries = []
    for entry in playlist['entries']:
        assert VIDEO_ID.fullmatch(entry['id']), entry['id']
        assert urlsplit(entry['url']).scheme == 'https' and urlsplit(entry['url']).hostname in {'www.youtube.com', 'youtube.com'}, entry['url']
        entries.append({**entry, 'courseId': str(entry['index']).zfill(3),
                        'guideId': video_groups.get(entry['id'])})
    data = {**{key: value for key, value in playlist.items() if key != 'entries'},
            'entries': entries, 'groups': groups}
    (out / 'catalog.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    print(f'Built full sysadmin playlist: {len(entries)} original videos, {len(groups)} bilingual topic guides')
