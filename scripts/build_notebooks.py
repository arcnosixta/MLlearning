"""Convert imported notebook cells into sanitized, static teaching pages.

No notebook code is executed. Original downloads stay byte-for-byte intact.
"""
import base64
import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit
import bleach
import markdown

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
TAGS={'p','br','hr','h1','h2','h3','h4','h5','h6','ul','ol','li','strong','b','em','i','u','s','del','a','img','table','thead','tbody','tr','th','td','pre','code','blockquote','div','span','sub','sup','dl','dt','dd'}
def attributes(tag,name,value):
    if name in ['title','alt']:return True
    if name=='href' and tag=='a':return urlsplit(value).scheme.lower() in ['https','http','mailto'] or value.startswith('#')
    if name=='src' and tag=='img':return value.startswith('course-assets/') or urlsplit(value).scheme.lower()=='https'
    return name in ['colspan','rowspan'] and tag in ['td','th'] and value.isdigit()
cleaner=bleach.Cleaner(tags=TAGS,attributes=attributes,protocols={'https','http','mailto'},strip=True)

def text(value):
    return value if isinstance(value,str) else ''.join(value or [])

def image_asset(data,mime):
    raw=base64.b64decode(re.sub(r'\s+','',text(data)),validate=True)
    if mime=='image/png':assert raw.startswith(b'\x89PNG\r\n\x1a\n');extension='png'
    else:assert mime=='image/jpeg' and raw.startswith(b'\xff\xd8');extension='jpg'
    relative=f'course-assets/{hashlib.sha256(raw).hexdigest()}.{extension}'
    path=OUT/relative;path.parent.mkdir(exist_ok=True);path.write_bytes(raw)
    return relative

def clean_markdown(source):
    # Export embedded bitmap illustrations rather than allowing arbitrary data URLs.
    source=re.sub(r'data:(image/(?:png|jpeg));base64,([A-Za-z0-9+/=\r\n]+)',lambda m:image_asset(m[2],m[1]),source)
    # Some source headings omit Markdown's separating space.
    source=re.sub(r'(?m)^(#{1,6})(?=[^#\s])',r'\1 ',source)
    rendered=markdown.markdown(source,extensions=['tables','fenced_code','sane_lists'])
    return cleaner.clean(rendered)

def build():
    manifest=json.loads((ROOT/'courses/sources.json').read_text(encoding='utf-8'))
    guides=json.loads((ROOT/'courses/path.json').read_text(encoding='utf-8'))
    assert len(manifest['items'])==len(guides)==7
    target=OUT/'file-lessons';target.mkdir(exist_ok=True)
    downloads=OUT/'notebooks';downloads.mkdir(exist_ok=True)
    catalog=[]
    for original,guide in zip(manifest['items'],guides):
        path=(ROOT/'courses'/original['path']).resolve()
        assert path.is_relative_to(ROOT/'courses')
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==original['sha256']
        notebook=json.loads(raw);cells=[];toc=[]
        for number,cell in enumerate(notebook['cells'],1):
            source=text(cell.get('source',[]))
            row={'number':number,'type':cell['cell_type']}
            if row['type']=='markdown':
                row['html']=clean_markdown(source)
                heading=re.search(r'(?m)^#{1,6}\s*(.+)',source)
                if heading:
                    label=re.sub(r'[*_`#]','',heading[1]).strip()
                    toc.append({'number':number,'title':label[:150]})
            else:
                row['source']=source;row['outputs']=[]
                for output in cell.get('outputs',[]):
                    data=output.get('data',{})
                    if 'image/png' in data or 'image/jpeg' in data:
                        mime='image/png' if 'image/png' in data else 'image/jpeg'
                        row['outputs'].append({'type':'image','src':image_asset(data[mime],mime)})
                    elif 'text/html' in data:
                        row['outputs'].append({'type':'html','html':cleaner.clean(text(data['text/html']))})
                    elif 'text/plain' in data or output.get('output_type')=='stream':
                        row['outputs'].append({'type':'text','text':text(data.get('text/plain',output.get('text',[])))})
                    elif output.get('output_type')=='error':
                        error=re.sub(r'\x1b\[[0-9;]*m','',text(output.get('traceback',[])))
                        row['outputs'].append({'type':'text','text':error})
            cells.append(row)
        filename=Path(original['path']).name;shutil.copy2(path,downloads/filename)
        common={'id':guide['id'],'mainLesson':guide['mainLesson'],'sourcePath':original['path'],'originalFilename':original['original_filename'],'download':'notebooks/'+filename,'cellCount':len(cells),'codeCount':sum(c['type']=='code' for c in cells),'sha256':original['sha256'],'ru':guide['ru'],'kk':guide['kk']}
        (target/(guide['id']+'.json')).write_text(json.dumps({'id':guide['id'],'cells':cells,'toc':toc},ensure_ascii=False),encoding='utf-8')
        catalog.append(common)
    (OUT/'file-course.json').write_text(json.dumps(catalog,ensure_ascii=False),encoding='utf-8')
    print(f'Built file pathway: {len(catalog)} notebooks, {sum(c["cellCount"] for c in catalog)} cells')

if __name__=='__main__':build()
