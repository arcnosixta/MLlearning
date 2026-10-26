"""Extract privately supplied teaching sources into ignored artifacts (never publish originals).

Optional tools: pip install pymupdf python-pptx olefile
Usage: python scripts/extract_java_sources.py --source-dir Q:/
PDF page numbers in the output are one-based physical pages, not printed labels.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path


def extract(path):
    if path.suffix.lower() == '.pdf':
        import pymupdf
        with pymupdf.open(path) as doc:
            return {'kind': 'pdf', 'outline': doc.get_toc(), 'units': [
                {'number': i + 1, 'text': page.get_text()} for i, page in enumerate(doc)]}
    if path.suffix.lower() == '.pptx':
        from pptx import Presentation
        return {'kind': 'pptx', 'units': [
            {'number': i + 1, 'text': '\n'.join(shape.text for shape in slide.shapes if shape.has_text_frame)}
            for i, slide in enumerate(Presentation(path).slides)]}
    import olefile
    # MS-PPT record tree: containers recurse; text atoms carry UTF-16LE or ANSI text.
    texts = []
    def records(data):
        position = 0
        while position + 8 <= len(data):
            flags, kind, length = struct.unpack_from('<HHI', data, position)
            start, end = position + 8, position + 8 + length
            if end > len(data):
                raise ValueError('Truncated PowerPoint record')
            payload = data[start:end]
            if flags & 15 == 15:
                records(payload)
            elif kind in (4000, 4026):
                texts.append(payload.decode('utf-16le', errors='replace'))
            elif kind == 4008:
                texts.append(payload.decode('cp1251', errors='replace'))
            position = end
    with olefile.OleFileIO(path) as doc:
        records(doc.openstream('PowerPoint Document').read())
    return {'kind': 'ppt', 'units': [{'number': i + 1, 'text': text} for i, text in enumerate(texts)]}


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('artifacts/java-sources'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name in ['Ihar_Blinou.Java.from.EPAM.2020.pdf', 'JAvaSlide.ppt', 'Жава қаз.pptx', 'Задачи.pdf']:
        path = args.source_dir / name
        data = {'filename': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), **extract(path)}
        target = args.output / (path.stem + '.json')
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'{name}: {len(data["units"])} pages/slides/text records')


if __name__ == '__main__':
    main()
