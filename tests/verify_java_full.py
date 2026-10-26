"""Compile every full-course example under Java 17 and check meaningful edge cases.

Optional real JDBC branch: python tests/verify_java_full.py --jdbc-jar /path/to/h2.jar
No PDF/PPT sources, credentials or external services are required for the baseline.
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jdbc-jar', type=Path)
args = parser.parse_args()
chapters = json.loads((ROOT / 'dist/java-full/catalog.json').read_text(encoding='utf-8'))
assert [c['id'] for c in chapters] == [f'{n:02d}' for n in range(1, 27)]
assert chapters == sorted(chapters, key=lambda c: c['id'])
sources = json.loads((ROOT / 'java/full/sources.json').read_text(encoding='utf-8'))
assert {s['id'] for s in sources['items']} == {'epam', 'slides-ru', 'slides-kk', 'problems'}
assert all(re.fullmatch('[0-9a-f]{64}', s['sha256']) for s in sources['items'])

probes = {
    '03': '''check(Main.gcd(0, 7)==7); check(Main.gcd(7, 0)==7); check(Main.gcd(0, 0)==0);
        try { Main.gcd(-1, 2); throw new AssertionError(); } catch (IllegalArgumentException expected) {}''',
    '04': '''int[][] inputs={{}, {2}, {1,2,2,5}, {-4,-2,0,3}};
        for (int[] a: inputs) for (int key=-6;key<=7;key++) {
            int expected=0; while(expected<a.length && a[expected]<key) expected++;
            check(Main.lowerBound(a,key)==expected);
        }''',
    '05': '''int[] values={-4,2,3}; check(Main.sum(values)==1);check(values[0]==-4);
        check(Main.sum()==0);check(Main.sum(Integer.MAX_VALUE,Integer.MAX_VALUE)==4294967294L);''',
    '06': '''Main.Wallet w=new Main.Wallet(10);check(!w.withdraw(11));check(w.balance()==10);
        check(w.withdraw(10));check(w.balance()==0);
        try {w.withdraw(0);throw new AssertionError();}catch(IllegalArgumentException expected){}
        try {new Main.Wallet(-1);throw new AssertionError();}catch(IllegalArgumentException expected){}''',
    '07': '''Main.Shape shape=new Main.Square(0);check(shape.area()==0);
        try {new Main.Square(Double.NaN);throw new AssertionError();}catch(IllegalArgumentException expected){}''',
    '08': '''var source=new java.util.ArrayList<>(java.util.List.of("A"));
        var ticket=new Main.Ticket(Main.State.NEW,source);source.add("B");check(ticket.items().size()==1);
        try {ticket.items().add("C");throw new AssertionError();}catch(UnsupportedOperationException expected){}''',
    '09': '''var a=new Main.Key("same");var b=new Main.Key("same");
        check(a.equals(b));check(a.hashCode()==b.hashCode());check(!a.equals(null));''',
    '13': '''var target=new java.util.ArrayList<Number>();target.add(0.5);
        Main.copy(java.util.List.of(1,2),target);check(target.equals(java.util.List.of(0.5,1,2)));
        Main.copy(java.util.List.<Integer>of(),target);check(target.size()==3);''',
    '25': '''check(Main.average(java.util.List.of()).isEmpty());
        check(Main.average(java.util.List.of(0)).orElseThrow()==0);
        check(Main.average(java.util.List.of(100)).orElseThrow()==100);
        check(Main.average(java.util.List.of(2,3)).orElseThrow()==2.5);
        for(int bad:new int[]{-1,101})try {Main.average(java.util.List.of(bad));throw new AssertionError();}catch(IllegalArgumentException expected){}''',
    '26': '''check(!Main.accepts(""));check(!Main.accepts("01x"));
        for(int length=1;length<=8;length++)for(int n=0;n<(1<<length);n++){
            String binary=String.format("%"+length+"s",Integer.toBinaryString(n)).replace(' ','0');
            check(Main.accepts(binary)==binary.endsWith("01"));
        }''',
}


def run(command, work):
    result = subprocess.run(command, cwd=work, capture_output=True, text=True, encoding='utf-8', timeout=45)
    assert result.returncode == 0, (command, result.stdout, result.stderr)
    return result.stdout.strip()


with tempfile.TemporaryDirectory() as temporary:
    for chapter in chapters:
        ident = chapter['id']
        source = ROOT / 'java/full' / ident
        work = Path(temporary) / ident
        work.mkdir()
        assert chapter['code'] == (source / 'Main.java').read_text(encoding='utf-8')
        assert chapter['code'] == (ROOT / 'dist/java-full' / ident / 'Main.java').read_text(encoding='utf-8')
        assert chapter['output'] == (source / 'output.txt').read_text(encoding='utf-8').strip()
        assert chapter['references'] and chapter['docs'].startswith('https://')
        assert chapter['weeks'] and all(n in range(1, 15) for n in chapter['weeks'])
        for lang, minimum in [('ru', 330), ('kk', 170)]:
            html = chapter[lang]['html']
            assert len(re.sub('<[^>]*>', ' ', html).split()) >= minimum, (ident, lang)
            assert len(re.findall('<h2>', html)) >= 3, (ident, lang)
            assert html.count('<details>') == 3 and html.count('<summary>') == 3
            assert all(html.count('{{answer:' + str(n) + '}}') == 1 for n in range(1, 4))
            assert '{{example}}' not in html and '<script' not in html.lower()
            assert chapter[lang]['title'] and chapter[lang]['description']
        assert chapter['ru']['html'] != chapter['kk']['html']
        (work / 'Main.java').write_text(chapter['code'], encoding='utf-8')
        run(['javac', '--release', '17', '-encoding', 'UTF-8', 'Main.java'], work)
        assert run(['java', '-Djava.awt.headless=true', '-cp', str(work), 'Main'], work) == chapter['output'], ident
        if ident in probes:
            (work / 'Probe.java').write_text('public class Probe { static void check(boolean v) { if(!v)throw new AssertionError(); } public static void main(String[] args) { ' + probes[ident] + ' } }', encoding='utf-8')
            run(['javac', '--release', '17', '-encoding', 'UTF-8', '-cp', str(work), 'Probe.java'], work)
            run(['java', '-cp', str(work), 'Probe'], work)
        if ident == '20' and args.jdbc_jar:
            classpath = str(work) + os.pathsep + str(args.jdbc_jar.resolve())
            assert run(['java', '-cp', classpath, 'Main', 'jdbc:h2:mem:course'], work) == chapter['output']
            print('PASS JDBC with real H2 database', flush=True)
        if chapter.get('lab'):
            with zipfile.ZipFile(ROOT / 'dist' / chapter['lab']) as archive:
                assert archive.read('src/main/java/Main.java').decode('utf-8') == chapter['code']
                assert 'pom.xml' in archive.namelist()
                assert 'src/test/java/MainTest.java' in archive.namelist()
                assert not any('..' in Path(name).parts or Path(name).is_absolute() for name in archive.namelist())
        print('PASS full Java chapter', ident, flush=True)
assert set().union(*(set(c['weeks']) for c in chapters)) == set(range(1, 15))
assert set().union(*(set(c['advanced']) for c in chapters)) == set(range(1, 14))
print('PASS 26 bilingual chapters, 78 exercises, 26 Java 17 examples and edge-case probes')
