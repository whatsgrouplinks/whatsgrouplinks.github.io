import json, re, html, os
RAW="team19_raw"
existing=set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
prev=json.load(open('team19_raw_all.json'))
seen={r['code'] for r in prev}
def clean(s):
    s=html.unescape(s or ''); s=re.sub(r'<[^>]+>',' ',s); s=re.sub(r'\s+',' ',s).strip(' -–—|•·\u00a0'); return s.strip()
records={}
def add(code, name, heading, source):
    code=code.strip().rstrip('/')
    if not code or len(code)<10 or code in records: return
    records[code]={'code':code,'name':clean(name)[:120],'heading':clean(heading)[:120],'source':source,'desc':''}
for fn in ["instant_home.html","wagroups_home.html","whtsp_home.html"]:
    t=open(os.path.join(RAW,fn),encoding='utf-8',errors='ignore').read()
    heads=[(m.start(), clean(m.group(1))) for m in re.finditer(r'<h[123][^>]*>(.*?)</h[123]>', t, re.S)]
    def heading_at(pos):
        h=''
        for p,txt in heads:
            if p<pos: h=txt
            else: break
        return h
    for m in re.finditer(r'<li[^>]*>(.*?)<a[^>]+href="https?://chat\.whatsapp\.com/([A-Za-z0-9_-]+)[^"]*"[^>]*>.*?</a>', t, re.S):
        add(m.group(2), m.group(1), heading_at(m.start()), fn.replace('.html',''))
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', t, re.S):
        row=m.group(1); lm=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', row)
        if not lm: continue
        tds=re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        add(lm.group(1), tds[0] if tds else '', heading_at(m.start()), fn.replace('.html',''))
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', t):
        if m.group(1) in records: continue
        ctx=clean(t[max(0,m.start()-300):m.start()])
        add(m.group(1), ctx[-100:], heading_at(m.start()), fn.replace('.html',''))
print("batch2 unique:", len(records))
fresh=[r for r in records.values() if r['code'] not in existing and r['code'] not in seen]
print("batch2 fresh (new vs existing+pass1):", len(fresh))
from collections import Counter
print(Counter(r['source'] for r in fresh))
print(Counter(r['heading'] for r in fresh).most_common(12))
json.dump(fresh, open('team19_fresh_batch2.json','w'), ensure_ascii=False, indent=1)
json.dump(list(records.values()), open('team19_raw_batch2.json','w'), ensure_ascii=False, indent=1)
