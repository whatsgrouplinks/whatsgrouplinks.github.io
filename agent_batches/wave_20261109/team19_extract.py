import json, re, html, os
from collections import defaultdict

RAW="team19_raw"
existing=set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
print("existing:", len(existing))

def norm(code):
    return code.strip().rstrip('/')

def clean(s):
    s=html.unescape(s or '')
    s=re.sub(r'<[^>]+>',' ',s)
    s=re.sub(r'\s+',' ',s).strip(' -–—|•·\u00a0')
    return s.strip()

records={}  # code -> dict
def add(code, name, heading, source, desc=''):
    code=norm(code)
    if not code or len(code)<10: return
    if code in records: return
    records[code]={'code':code,'name':clean(name)[:120],'heading':clean(heading)[:120],'source':source,'desc':clean(desc)[:300]}

# --- 1. Groupsor API (structured) ---
d=json.load(open(f'{RAW}/groupssor_api.json'))
for x in d:
    if str(x.get('platform','')).lower()!='whatsapp': continue
    m=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', x.get('inviteLink','') or '')
    if not m: continue
    add(m.group(1), x.get('name',''), x.get('category','') or '', 'groupssor-api', x.get('description',''))
print("after groupsor:", len(records))

# --- 2. HTML files: li/tr context + nearest heading ---
CATMAP={'pakistani girls':'PK','girls':'Friendship','jobs':'Jobs','business':'Business','education':'Education',
 'entertainment':'Entertainment','gaming':'Gaming','sports':'Sports','funny':'Funny','news':'News',
 'islamic':'Islamic','technology':'Technology','health':'Health','friendship':'Friendship','international':'Community & Social'}

for fn in sorted(os.listdir(RAW)):
    if not fn.endswith('.html'): continue
    t=open(os.path.join(RAW,fn),encoding='utf-8',errors='ignore').read()
    src=fn.replace('.html','')
    # headings with positions
    heads=[(m.start(), clean(m.group(1))) for m in re.finditer(r'<h[123][^>]*>(.*?)</h[123]>', t, re.S)]
    def heading_at(pos):
        h=''
        for p,txt in heads:
            if p<pos: h=txt
            else: break
        return h
    # <li>...<a href=chat...> pattern
    for m in re.finditer(r'<li[^>]*>(.*?)<a[^>]+href="https?://chat\.whatsapp\.com/([A-Za-z0-9_-]+)[^"]*"[^>]*>.*?</a>', t, re.S):
        add(m.group(2), m.group(1), heading_at(m.start()), src)
    # table rows: <tr>...name...</tr> containing link
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', t, re.S):
        row=m.group(1)
        lm=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', row)
        if not lm: continue
        # name = first td text
        tds=re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        name=tds[0] if tds else ''
        add(lm.group(1), name, heading_at(m.start()), src)
    # generic: any remaining chat link, take preceding 200 chars stripped
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', t):
        code=m.group(1)
        if code in records: continue
        ctx=clean(t[max(0,m.start()-300):m.start()])
        add(code, ctx[-100:], heading_at(m.start()), src)
print("after html:", len(records))

json.dump(list(records.values()), open('team19_raw_all.json','w'), ensure_ascii=False, indent=1)
fresh=[r for r in records.values() if r['code'] not in existing]
print("TOTAL unique:", len(records), "FRESH (not in existing):", len(fresh))
from collections import Counter
print("fresh by source:", Counter(r['source'] for r in fresh))
print("fresh by heading top:", Counter(r['heading'] for r in fresh).most_common(15))
json.dump(fresh, open('team19_fresh_raw.json','w'), ensure_ascii=False, indent=1)
