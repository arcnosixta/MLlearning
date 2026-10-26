"""Publish authored bilingual Markdown chapters and independent Java 17 examples."""
import json
import re
import shutil
import zipfile
from pathlib import Path

import bleach
import markdown

ROOT = Path(__file__).resolve().parents[1]


def build():
    source = ROOT / 'java/full'
    out = ROOT / 'dist/java-full'
    out.mkdir(parents=True, exist_ok=True)
    syllabus = json.loads((source / 'catalog.json').read_text(encoding='utf-8'))
    cleaner = bleach.Cleaner(
        tags={'p', 'h2', 'h3', 'h4', 'pre', 'code', 'ul', 'ol', 'li', 'strong', 'em',
              'blockquote', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'details', 'summary'},
        attributes={'a': ['href', 'title']}, protocols={'https', 'http'}, strip=True)
    chapters = []
    for entry in syllabus:
        folder = source / entry['id']
        if not folder.exists():
            continue  # Chapters can be authored incrementally; coverage is verified by tests.
        code = (folder / 'Main.java').read_text(encoding='utf-8')
        output = (folder / 'output.txt').read_text(encoding='utf-8').strip()
        item = {**entry, 'code': code, 'output': output}
        for lang in ['ru', 'kk']:
            text = (folder / f'{lang}.md').read_text(encoding='utf-8')
            title, body = text.split('\n', 1)
            assert title.startswith('# '), folder
            assert body.count('{{example}}') == 1, folder
            assert all(body.count('{{answer:' + str(i) + '}}') == 1 for i in range(1, 4)), folder
            label = 'Ожидаемый вывод' if lang == 'ru' else 'Күтілетін нәтиже'
            example = '\n```java\n' + code.rstrip() + '\n```\n\n**' + label + ':**\n\n```text\n' + output + '\n```\n'
            body = body.replace('{{example}}', example)
            rendered = cleaner.clean(markdown.markdown(body, extensions=['fenced_code', 'tables', 'sane_lists']))
            item[lang] = {'title': title[2:].strip(), 'html': rendered,
                          'description': re.sub(r'[*`]', '', body.strip().split('\n')[0])}
        target = out / entry['id']
        target.mkdir(exist_ok=True)
        shutil.copy2(folder / 'Main.java', target / 'Main.java')
        if (folder / 'lab').exists():
            # Fixed timestamps/order keep the downloadable lab byte-for-byte reproducible.
            with zipfile.ZipFile(target / 'lab.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
                files = {'src/main/java/Main.java': (folder / 'Main.java').read_bytes()}
                files.update({p.relative_to(folder / 'lab').as_posix(): p.read_bytes()
                              for p in sorted((folder / 'lab').rglob('*')) if p.is_file()})
                for name, data in sorted(files.items()):
                    info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, data)
            item['lab'] = f'java-full/{entry["id"]}/lab.zip'
        chapters.append(item)
    (out / 'catalog.json').write_text(json.dumps(chapters, ensure_ascii=False), encoding='utf-8')
    shutil.copy2(source / 'sources.json', out / 'sources.json')
    print(f'Built {len(chapters)} full bilingual Java chapters')
