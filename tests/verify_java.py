"""Compile and execute all semester examples and all 42 trace questions."""
import json
import subprocess
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
weeks=json.loads((ROOT/'dist/java-course.json').read_text(encoding='utf-8'))
assert [w['id'] for w in weeks]==[f'{n:02d}' for n in range(1,15)]
assert 'abstract' in weeks[6]['code']
seen=set()
with tempfile.TemporaryDirectory() as temporary:
    path=Path(temporary)
    def execute(code):
        (path/'Main.java').write_text(code,encoding='utf-8')
        compile_result=subprocess.run(['javac','--release','17','-encoding','UTF-8','-d',str(path),str(path/'Main.java')],capture_output=True,text=True,timeout=30)
        assert compile_result.returncode==0,compile_result.stderr
        result=subprocess.run(['java','-cp',str(path),'Main'],cwd=path,capture_output=True,text=True,timeout=15)
        assert result.returncode==0,result.stderr
        return result.stdout.strip()
    for week in weeks:
        assert len(week['questions'])==6
        assert len(week['ru']['sections'])==len(week['kk']['sections'])==3
        assert week['code']==(ROOT/'dist/java-examples'/week['id']/'Main.java').read_text(encoding='utf-8')
        assert execute(week['code'])==week['output'].strip(),week['id']
        for q in week['questions']:
            assert q['id'] not in seen;seen.add(q['id'])
            assert q['week']==week['week']
            for lang in ['ru','kk']:
                assert len(q[lang]['options'])==3 and q[lang]['explanation']
                assert q['answer'] in range(3)
            if 'trace' in q:
                actual=execute('public class Main { public static void main(String[] args) { '+q['trace']+' } }')
                assert actual==q['ru']['options'][q['answer']],(q['id'],actual)
        print('PASS Java week',week['id'],'example + 3 executable trace questions',flush=True)
assert len(seen)==84
print('PASS 14 Java examples and 42 traces under --release 17')
