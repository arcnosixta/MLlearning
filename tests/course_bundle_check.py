"""Archives must contain every runnable source and verify their declared contents."""
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
for course,count,filename in [('java',26,'Main.java'),('sysadmin',35,'lab.sh')]:
    with zipfile.ZipFile(ROOT/'dist'/(course+'-full')/'study.zip') as archive:
        names=archive.namelist()
        for line in archive.read('MANIFEST.sha256').decode().splitlines():
            digest,name=line.split('  ',1)
            assert hashlib.sha256(archive.read(name)).hexdigest()==digest
        assert all('..' not in Path(name).parts and not name.startswith('/') for name in names)
        for number in range(1,count+1):
            ident=f'{number:02d}'
            source=ROOT/course/'full'
            if course=='sysadmin':source/='guides'
            assert archive.read(ident+'/'+filename).decode()==(source/ident/filename).read_text(encoding='utf-8')
            assert '{{example}}' not in archive.read(ident+'/ru.md').decode()
            assert '{{answer:' not in archive.read(ident+'/kk.md').decode()
        if course=='sysadmin':assert archive.read('PLAYLIST.md').decode().count('https://www.youtube.com/watch?v=')==106
    print('PASS complete',course,'study bundle and SHA256 manifest')
