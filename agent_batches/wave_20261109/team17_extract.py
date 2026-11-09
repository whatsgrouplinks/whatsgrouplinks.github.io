import re, json, os, html
from collections import OrderedDict
RAW='team17_raw'
existing=set(json.load(open('../../.existing_codes.json')))
pat=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{10,30})')
out={}
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith('.html'): continue
    src=fn[:-5]
    txt=open(os.path.join(RAW,fn),encoding='utf-8',errors='ignore').read()
    # strip scripts/styles for context readability but keep hrefs
    for m in pat.finditer(txt):
        code=m.group(1).rstrip('/')
        if code in out: 
            out[code]['sources'].append(src); continue
        start=max(0,m.start()-400); end=min(len(txt),m.end()+100)
        ctx=html.unescape(re.sub(r'<[^>]+>',' ',txt[start:end]))
        ctx=re.sub(r'\s+',' ',ctx).strip()
        out[code]={'code':code,'sources':[src],'ctx':ctx[:300]}
print('total distinct codes in fetched pages:',len(out))
fresh={c:v for c,v in out.items() if c not in existing}
print('fresh vs existing union:',len(fresh),'| already in union:',len(out)-len(fresh))
json.dump(out,open('team17_extracted_raw.json','w'),ensure_ascii=False,indent=1)
json.dump(fresh,open('team17_fresh_raw.json','w'),ensure_ascii=False,indent=1)
# per-source counts
from collections import Counter
c=Counter()
for v in fresh.values():
    for s in v['sources']: c[s]+=1
print('fresh per source:',dict(c))
