"""Validate every new module and run examples only in compatible runtimes."""
import json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tracks=json.loads((ROOT/'dist/tracks.json').read_text(encoding='utf-8'))
assert {t['id'] for t in tracks}=={'go','onec','java-advanced','sysadmin'}
seen=set()
with tempfile.TemporaryDirectory() as temporary:
    work=Path(temporary)
    for track in tracks:
        assert len(track['lessons'])==6
        for lesson in track['lessons']:
            for lang in ['ru','kk']:
                t=lesson[lang]
                assert len(t['sections'])==3 and len(t['criteria'])==3
                assert t['task'] and t['context'] and t['intro']
                assert all(len(s['text'])>120 for s in t['sections'])
            assert len(lesson['questions'])==5 and lesson['terminal']['answers']
            for q in lesson['questions']:
                assert q['id'] not in seen;seen.add(q['id'])
                assert q['week']==lesson['week']
                for lang in ['ru','kk']:
                    assert len(q[lang]['options'])==3 and q[lang]['explanation']
                assert q['answer'] in range(3)
            source=ROOT/'dist/track-examples'/track['id']/lesson['id']/track['filename']
            assert source.read_text(encoding='utf-8')==lesson['code']
            def run(args,timeout=120):
                result=subprocess.run(args,cwd=work,capture_output=True,text=True,encoding='utf-8',timeout=timeout,env=dict(os.environ,GOWORK='off',GOTOOLCHAIN='local',GO111MODULE='off'))
                assert result.returncode==0,(track['id'],lesson['id'],result.stderr)
                return result.stdout.strip()
            if track['id']=='go':
                assert run(['go','run',str(source)])==lesson['output'].strip()
            elif track['id']=='java-advanced':
                run(['javac','--release','17','-encoding','UTF-8','-d',str(work),str(source)])
                assert run(['java','-cp',str(work),'Main'])==lesson['output'].strip()
            elif track['id']=='sysadmin':
                bash='C:/Program Files/Git/bin/bash.exe' if os.name=='nt' else 'bash'
                run([bash,'-n',str(source)])
                if os.name!='nt':assert run([bash,str(source)])==lesson['output'].strip()
            else:
                # 1C requires a proprietary runtime and specified metadata, not CLI execution.
                assert 'Функция' in lesson['code'] or 'Процедура' in lesson['code']
                assert len(lesson['ru']['context'])>70
            print('PASS',track['id'],lesson['id'],flush=True)
assert len(seen)==120
print('PASS 24 bilingual modules, 120 questions and compatible example runtimes; 1C not executed')
