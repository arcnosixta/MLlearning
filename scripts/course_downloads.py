"""Deterministic study archives with portable text and a verifiable file manifest."""
import hashlib
from pathlib import PurePosixPath
import zipfile


def write_study_bundle(target, files, readme):
    contents = {**files, 'README.md': readme.encode('utf-8')}
    for name in contents:
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ValueError('Unsafe study archive path')
    contents['MANIFEST.sha256'] = ''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n'
                                         for name, data in sorted(contents.items())).encode('utf-8')
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


def standalone_markdown(text, example):
    result = text.replace('{{example}}', example)
    for number in range(1, 4):
        result = result.replace('{{answer:' + str(number) + '}}', '\n________________________\n')
    return result.encode('utf-8')
