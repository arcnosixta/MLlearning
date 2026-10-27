"""Publish authored bilingual Markdown chapters and independent Java 17 examples."""
import json
import re
import shutil
import zipfile
from pathlib import Path

import bleach
import markdown
from validate_full_sources import validate_java
from course_downloads import write_study_bundle, standalone_markdown

ROOT = Path(__file__).resolve().parents[1]


def build():
    source = ROOT / 'java/full'
    out = ROOT / 'dist/java-full'
    syllabus = json.loads((source / 'catalog.json').read_text(encoding='utf-8'))
    validate_java(source, syllabus)
    out.mkdir(parents=True, exist_ok=True)
    cleaner = bleach.Cleaner(
        tags={'p', 'h2', 'h3', 'h4', 'pre', 'code', 'ul', 'ol', 'li', 'strong', 'em',
              'blockquote', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'details', 'summary'},
        attributes={'a': ['href', 'title']}, protocols={'https', 'http'}, strip=True)
    chapters = []
    bundled = {}
    for entry in syllabus:
        folder = source / entry['id']
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
            bundled[f'{entry["id"]}/{lang}.md'] = standalone_markdown(text, example)
            rendered = cleaner.clean(markdown.markdown(body, extensions=['fenced_code', 'tables', 'sane_lists']))
            item[lang] = {'title': title[2:].strip(), 'html': rendered,
                          'description': re.sub(r'[*`]', '', body.strip().split('\n')[0])}
        target = out / entry['id']
        target.mkdir(exist_ok=True)
        shutil.copy2(folder / 'Main.java', target / 'Main.java')
        bundled[f'{entry["id"]}/Main.java'] = code.encode('utf-8')
        bundled[f'{entry["id"]}/output.txt'] = (output + '\n').encode('utf-8')
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
            bundled[f'{entry["id"]}/lab.zip'] = (target / 'lab.zip').read_bytes()
        chapters.append(item)
        # Write again after optional lab metadata has been attached.
        (target / 'chapter.json').write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
    (out / 'catalog.json').write_text(json.dumps(chapters, ensure_ascii=False), encoding='utf-8')
    index = [{key: value for key, value in item.items() if key not in {'code', 'output', 'ru', 'kk'}} |
             {lang: {key: value for key, value in item[lang].items() if key != 'html'} for lang in ['ru', 'kk']}
             for item in chapters]
    (out / 'index.json').write_text(json.dumps(index, ensure_ascii=False), encoding='utf-8')
    shutil.copy2(source / 'sources.json', out / 'sources.json')
    write_study_bundle(out / 'study.zip', bundled, '''# Java — учебный архив / оқу архиві

26 независимых примеров и русские/казахские разборы. Нужен JDK 17+.
Распакуй архив в отдельную папку. Каждый Main запускается отдельно:

```sh
javac --release 17 -encoding UTF-8 01/Main.java
java -cp 01 Main
```

Ожидаемый вывод — в output.txt соответствующей главы, теория и задачи — в ru.md/kk.md.
Основные примеры не требуют внешних библиотек. Глава20 без аргумента не исполняет SQL;
реальная JDBC-лабораторная требует H2. GUI главы24 требует экрана только с --window.
Дополнительная Maven-лабораторная: распакуй25/lab.zip отдельно, затем mvn test.
Решения в Markdown заполняются самостоятельно; браузерный прогресс в этот архив не входит.

При наличии sha256sum: `sha256sum -c MANIFEST.sha256` проверяет целостность файлов.
Java мысалдарын әр каталогтан бөлек орында. Нәтиже output.txt ішінде.
''')
    print(f'Built {len(chapters)} full bilingual Java chapters')
