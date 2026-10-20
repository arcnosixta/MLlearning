"""Coverage, teaching structure and first-run examples, independent of notebook originals."""
import json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'dist/teaching.json').read_text(encoding='utf-8'))
limits={'ml':24,'files':7,'java':14,'go':13,'onec':13,'java-advanced':13,'sysadmin':13}
expected={(path,ident) for path,count in limits.items() for ident in ['start']+[f'{n:02d}' for n in range(1,count+1)]}
assert len(data)==104 and {(x['path'],x['id']) for x in data}==expected
assert len({(x['path'],x['id']) for x in data})==len(data)
texts={lang:set() for lang in ['ru','kk']}
with tempfile.TemporaryDirectory() as temporary:
    for item in data:
        for lang in ['ru','kk']:
            t=item[lang]
            assert len(t['explain'])>=2 and len(t['terms'])>=2 and len(t['walkthrough'])>=3
            assert all(len(p)>70 for p in t['explain'])
            assert len(t['exercises'])==2 and all(e['prompt'] and e['hint'] and e['solution'] for e in t['exercises'])
            teaching_text=t['explain']+t['walkthrough']+[t['mistake']]+[v['meaning'] for v in t['terms']]+[e[k] for e in t['exercises'] for k in ['prompt','hint','solution']]
            assert len(' '.join(teaching_text).split())>=(120 if lang=='ru' else 100),(item['path'],item['id'],lang)
            # Explanations must be authored for each topic, not cloned paragraphs with a title swap.
            fingerprint=' '.join(t['explain']);assert fingerprint not in texts[lang];texts[lang].add(fingerprint)
            assert item['ru']['explain']!=item['kk']['explain']
        if item['id']!='start':continue
        source=ROOT/'dist/teaching-examples'/item['path']/item['filename']
        assert source.read_text(encoding='utf-8')==item['code']
        for attachment in item.get('attachments',[]):
            assert (ROOT/'dist/teaching-examples'/item['path']/attachment['filename']).read_text(encoding='utf-8')==attachment['code']
        def run(args):
            r=subprocess.run(args,cwd=temporary,text=True,capture_output=True,encoding='utf-8',timeout=90,env=dict(os.environ,GO111MODULE='off',GOWORK='off',GOTOOLCHAIN='local'))
            assert r.returncode==0,(item['path'],r.stderr)
            return r.stdout.strip()
        if item['path'] in ['ml','files']:actual=run(['python',str(source)])
        elif item['path']=='go':actual=run(['go','run',str(source)])
        elif item['path'] in ['java','java-advanced']:
            run(['javac','--release','17','-encoding','UTF-8','-d',temporary,str(source)])
            actual=run(['java','-cp',temporary,'Main'])
        elif item['path']=='sysadmin':actual=run(['C:/Program Files/Git/bin/bash.exe' if os.name=='nt' else 'bash',str(source)])
        else:
            assert 'Процедура' in item['code'] and item['ru']['runtime'];continue
        assert actual==item['output'].strip(),(item['path'],actual,item['output'])
        print('PASS first file',item['path'],flush=True)
print('PASS 97 topic-specific bilingual guides and 7 introductory lessons; 1C runtime unavailable')
