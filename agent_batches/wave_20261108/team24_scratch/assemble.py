import json, re, html, sys
sys.path.insert(0,'.')
from build_records import map_cat, blocked, clean_name, desc_for
union=set(json.load(open('../dedupe_union.json')))
verified=[]; pending=[]; dropped=[]
seen_codes=set()
def add(code, name, cat_raw, country, desc_hint='', source=''):
    if not code or len(code)!=22: return
    if code in union: return
    if code in seen_codes:
        dropped.append((code,'dup-in-team',source)); return
    name=clean_name(name)
    if not name: return
    b=blocked(name, desc_hint)
    if b:
        dropped.append((code,b,source)); return
    cat=map_cat(cat_raw, name)
    if cat not in ['Education','Jobs','Entertainment','Islamic','News','Sports','Technology','Health','Business','Gaming','Friendship','Community & Social','Online Earning','Crypto','Cooking','Poetry','Travel','Scholarship','Freelance','Real Estate','Buy & Sell','Finance','Funny']:
        cat='Community & Social'
    desc=desc_hint.strip() if desc_hint and len(desc_hint.strip())>20 else desc_for(name,cat,country)
    desc=html.unescape(re.sub(r'\s+',' ',desc)).strip()
    if len(desc)>300: desc=desc[:297]+'...'
    verified.append({'name':name,'category':cat,'country':country,'description':desc,
                     'invite':f'https://chat.whatsapp.com/{code}','image':''})
    seen_codes.add(code)
# 1) vagasproximas + mde (verified_vagas_mde.json)
vm=json.load(open('verified_vagas_mde.json'))
for code,r in vm.items():
    if r['verify']!='live': continue
    if r['source']=='vagasproximas':
        add(code, r['ogtitle'] or r['name'], 'vagas', 'BR', '', 'vagasproximas')
    else:
        raw=r['name']
        # label like 'Football (Men) Sports' -> last word is category hint
        cat_hint=raw.split()[-1] if raw else ''
        add(code, r['ogtitle'] or raw, cat_hint, 'CO', '', 'mde')
    if r['verify']=='transport':
        pending.append({'name':clean_name(r['name']),'category':map_cat(''),'country':'BR' if r['source']=='vagasproximas' else 'CO','description':'','invite':f'https://chat.whatsapp.com/{code}','image':'','reason':'transport'})
# 2) tugrupo
tu=json.load(open('verified_tugrupo.json'))
recs=json.load(open('tugrupo_raw.json'))
code2rec={}
for u,r in recs.items():
    if r.get('code'): code2rec.setdefault(r['code'],(u,r))
for code,r in tu.items():
    if r['verify']=='transport':
        u,rec=code2rec[code]
        pending.append({'name':clean_name(rec.get('title','')),'category':map_cat(rec.get('cat','')),'country':'International','description':'','invite':f'https://chat.whatsapp.com/{code}','image':'','reason':'transport'})
        continue
    if r['verify']!='live': continue
    u,rec=code2rec[code]
    # name: og:title preferred; strip surrounding quotes
    name=(r['ogtitle'] or '').strip().strip('"').strip()
    if not name:
        t=rec.get('title','')
        name=re.sub(r'^"?(.*?)"?\s*Grupo de WhatsApp\s*$',r'\1',t).strip()
    add(code, name, rec.get('cat',''), 'International', '', 'tugrupo')
# 3) linkado (if file exists)
try:
    lk=json.load(open('verified_linkado.json'))
    raw=json.load(open('linkado_raw.json'))
    page2rec={u:v for u,v in raw.items()}
    fresh=json.load(open('linkado_fresh.json'))
    for code,r in lk.items():
        if r['verify']=='transport':
            rec=page2rec.get(r['page'],{})
            pending.append({'name':clean_name(rec.get('title','')),'category':'Community & Social','country':'BR','description':'','invite':f'https://chat.whatsapp.com/{code}','image':'','reason':'transport'})
            continue
        if r['verify']!='live': continue
        rec=page2rec.get(r['page'],{})
        t=rec.get('title','')
        # title: 'Grupo de WhatsApp <name> - <category>'
        m=re.match(r'Grupo de WhatsApp (.+?)\s*-\s*(.+)$', t)
        lname=m.group(1).strip() if m else t
        lcat=m.group(2).strip() if m else ''
        name=(r['ogtitle'] or '').strip() or lname
        add(code, name, lcat, 'BR', rec.get('desc',''), 'linkado')
    print('linkado included')
except FileNotFoundError:
    print('linkado verified file NOT present - skipping linkado')
print('verified:',len(verified),'pending:',len(pending),'dropped:',len(dropped))
for d in dropped: print('  DROP',d)
json.dump(verified,open('team24_verified_draft.json','w'),ensure_ascii=False,indent=1)
json.dump(pending,open('team24_pending_draft.json','w'),ensure_ascii=False,indent=1)
# category + country tallies
from collections import Counter
print(Counter([v['category'] for v in verified]))
print(Counter([v['country'] for v in verified]))
