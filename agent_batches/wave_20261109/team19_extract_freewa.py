import json, re, html, os, glob
RAW="team19_raw"
existing=set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
seen={r['code'] for r in json.load(open('team19_raw_all.json'))}
urls=open(f'{RAW}/freewa_post_urls.txt').read().splitlines()
def clean(s):
    s=html.unescape(s or ''); s=re.sub(r'<[^>]+>',' ',s); s=re.sub(r'\s+',' ',s).strip(' -–—|•·\u00a0'); return s.strip()
recs={}
for i,u in enumerate(urls,1):
    f=f'{RAW}/freewa_posts/p{i:03d}.html'
    if not os.path.exists(f): continue
    t=open(f,encoding='utf-8',errors='ignore').read()
    slug=u.rstrip('/').split('/')[-1]
    # title
    mt=re.search(r'<title>(.*?)</title>', t, re.S)
    title=clean(mt.group(1)) if mt else slug
    title=re.sub(r'\s*[-–|]\s*Free WA.*$','',title,flags=re.I)
    # first chat link + surrounding context
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', t):
        code=m.group(1).strip().rstrip('/')
        if code in recs: continue
        recs[code]={'code':code,'name':title[:120],'heading':slug,'source':'freewagroup','desc':''}
print("freewa unique codes:", len(recs))
fresh=[r for r in recs.values() if r['code'] not in existing and r['code'] not in seen]
print("freewa fresh:", len(fresh))
json.dump(list(recs.values()), open('team19_raw_freewa.json','w'), ensure_ascii=False, indent=1)
json.dump(fresh, open('team19_fresh_freewa.json','w'), ensure_ascii=False, indent=1)
# prescreen same rules
DROP_RE = re.compile(r'\b(xxx|porn|sex|sexy|escort|cam[- ]?girl|hookup|hook[- ]?up|nude|naked|erotic|adult\s*(video|pic|content)|b-?love|forsage|sheyi|airdrop|free\s*money|onlyfans|call\s*girl|randi|desi\s*sex|hot\s*girl|hot\s*video|leak(ed)?\s*(video|mms)|mms\s*leak)\b', re.I)
kept=[r for r in fresh if not DROP_RE.search(r['name']+' '+r['heading'])]
print("freewa kept after prescreen:", len(kept), "dropped:", len(fresh)-len(kept))
for r in fresh:
    if r not in kept: print(" DROP", r['code'], r['name'][:70], "|", r['heading'])
json.dump(kept, open('team19_freewa_to_verify.json','w'), ensure_ascii=False, indent=1)
