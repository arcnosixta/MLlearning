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
from validate_full_sources import validate_sysadmin
from course_downloads import write_study_bundle, standalone_markdown

ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')


def build():
    source = ROOT / 'sysadmin/full'
    playlist = json.loads((source / 'playlist.json').read_text(encoding='utf-8'))
    definitions = json.loads((source / 'groups.json').read_text(encoding='utf-8'))
    validate_sysadmin(source, playlist, definitions)
    paths = json.loads((source / 'paths.json').read_text(encoding='utf-8'))
    briefs = json.loads((source / 'briefs.json').read_text(encoding='utf-8'))
    review = json.loads((source / 'review.json').read_text(encoding='utf-8'))
    if [question['id'] for question in review] != [group['id'] for group in definitions]:
        raise ValueError('Every topic needs one scenario review question')
    for question in review:
        if type(question['answer']) is not int or question['answer'] not in range(3):
            raise ValueError('Invalid review answer')
        for lang in ['ru', 'kk']:
            text = question[lang]
            if not text['question'] or not text['explanation'] or len(text['options']) != 3 or len(set(text['options'])) != 3:
                raise ValueError('Incomplete bilingual review question')
    if [brief['id'] for brief in briefs] != [f'{n:03d}' for n in range(1, 107)]:
        raise ValueError('Every video needs its own ordered learning brief')
    for lang in ['ru', 'kk']:
        for field in ['goal', 'check']:
            values = [brief[lang][field] for brief in briefs]
            if any(not value.strip() for value in values) or len(set(values)) != 106:
                raise ValueError('Learning briefs must be specific to every video')
    known = {group['id'] for group in definitions}
    if len({path['id'] for path in paths}) != len(paths) or any(not path['groups'] or len(set(path['groups'])) != len(path['groups']) or not set(path['groups']) <= known for path in paths):
        raise ValueError('Invalid learning pathway')
    out = ROOT / 'dist/sysadmin-full'
    out.mkdir(parents=True, exist_ok=True)
    cleaner = bleach.Cleaner(
        tags={'p', 'h2', 'h3', 'h4', 'pre', 'code', 'ul', 'ol', 'li', 'strong', 'em',
              'blockquote', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'details', 'summary'},
        attributes={'a': ['href', 'title']}, protocols={'https', 'http'}, strip=True)
    groups = []
    bundled = {}
    video_groups = {}
    for definition in definitions:
        ident = definition['id']
        assert re.fullmatch(r'\d{2}', ident), ident
        folder = source / 'guides' / ident
        code = (folder / 'lab.sh').read_text(encoding='utf-8')
        output = (folder / 'output.txt').read_text(encoding='utf-8').strip()
        download = f'sysadmin-full/labs/{ident}/lab.sh'
        item = {**definition, 'code': code, 'output': output, 'download': download, 'review': review[int(ident)-1]}
        for lang in ['ru', 'kk']:
            raw = (folder / f'{lang}.md').read_text(encoding='utf-8')
            title, body = raw.split('\n', 1)
            assert title.startswith('# '), (ident, lang)
            assert body.count('{{example}}') == 1, (ident, lang)
            assert all(body.count('{{answer:' + str(n) + '}}') == 1 for n in range(1, 4)), (ident, lang)
            label = 'Ожидаемый вывод' if lang == 'ru' else 'Күтілетін нәтиже'
            example = '\n```bash\n' + code.rstrip() + '\n```\n\n**' + label + ':**\n\n```text\n' + output + '\n```\n'
            body = body.replace('{{example}}', example)
            bundled[f'{ident}/{lang}.md'] = standalone_markdown(raw, example)
            rendered = cleaner.clean(markdown.markdown(body, extensions=['fenced_code', 'tables', 'sane_lists']))
            item[lang] = {'title': title[2:].strip(), 'html': rendered,
                          'description': re.sub(r'[*`]', '', body.strip().split('\n')[0])}
        target = out / 'labs' / ident
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(folder / 'lab.sh', target / 'lab.sh')
        bundled[f'{ident}/lab.sh'] = code.encode('utf-8')
        bundled[f'{ident}/output.txt'] = (output + '\n').encode('utf-8')
        for video in definition['videoIds']:
            assert VIDEO_ID.fullmatch(video), video
            assert video not in video_groups, ('Video assigned twice', video)
            video_groups[video] = ident
        groups.append(item)
        guide_out = out / 'guides'
        guide_out.mkdir(exist_ok=True)
        (guide_out / (ident + '.json')).write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
    entries = []
    for entry in playlist['entries']:
        assert VIDEO_ID.fullmatch(entry['id']), entry['id']
        assert urlsplit(entry['url']).scheme == 'https' and urlsplit(entry['url']).hostname in {'www.youtube.com', 'youtube.com'}, entry['url']
        item = {**entry, 'courseId': str(entry['index']).zfill(3),
                'guideId': video_groups.get(entry['id']), 'brief': briefs[entry['index']-1]}
        lesson_out = out / 'lessons'
        lesson_out.mkdir(exist_ok=True)
        (lesson_out / (item['courseId'] + '.json')).write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
        entries.append(item)
    data = {**{key: value for key, value in playlist.items() if key != 'entries'},
            'entries': entries, 'groups': groups, 'paths': paths}
    (out / 'catalog.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    summaries = [{key: value for key, value in group.items() if key not in {'code', 'output', 'ru', 'kk', 'review'}} |
                 {lang: {key: value for key, value in group[lang].items() if key != 'html'} for lang in ['ru', 'kk']}
                 for group in groups]
    index_entries = [{key: value for key, value in entry.items() if key != 'brief'} for entry in entries]
    (out / 'index.json').write_text(json.dumps({**data, 'groups': summaries, 'entries': index_entries}, ensure_ascii=False), encoding='utf-8')
    (out / 'review.json').write_text(json.dumps(review, ensure_ascii=False), encoding='utf-8')
    bundled['PLAYLIST.md'] = ('# Оригинальные видео / Түпнұсқа бейнелер\n\n' + '\n'.join(
        f'{entry["courseId"]}. [{entry["title"]}]({entry["url"]}) — {entry["duration"]}' for entry in entries)).encode('utf-8')
    write_study_bundle(out / 'study.zip', bundled, '''# Linux — учебный архив / оқу архиві

35 Bash-примеров, ожидаемые результаты и RU/ҚАЗ разборы. Видео остаются на YouTube;
в PLAYLIST.md находятся все106 исходных ссылок, для просмотра нужен интернет.

Распакуй в отдельную папку. Нужны Bash4+, awk, sed, grep, sort, coreutils;
для29/lab.sh также нужен OpenSSL с проверкой имени сертификата.
В Linux/WSL/Git Bash выполни:

```sh
bash 01/lab.sh
```

Сравни вывод с01/output.txt. Примеры не требуют root, сети или реальных служб.
Большинство моделируют состояние на фиксированных учебных данных; они не заменяют
серверную лабораторную на VM. Скрипт29 создаёт только временный учебный сертификат.
Не запускай Bash-файлы через PowerShell как PowerShell-код.
Реальные настройки дисков, firewall, SSH, sudo/PAM изучаются на отдельном стенде.
Прогресс сайта и личные ответы не входят в архив: экспортируй их в разделе данных.

При наличии sha256sum: `sha256sum -c MANIFEST.sha256` проверяет целостность файлов.
Әр бөлімнің lab.sh файлын Bash ішінде орындап, output.txt нәтижесімен салыстыр.
''')
    print(f'Built full sysadmin playlist: {len(entries)} original videos, {len(groups)} bilingual topic guides')
