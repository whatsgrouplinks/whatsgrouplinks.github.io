import requests, re, json, time
from html import unescape
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
def fetch(u, t=25):
    return requests.get(u, headers=UA, timeout=t)
def clean(s):
    s=unescape(re.sub(r'<[^>]+>','',s or '')).strip()
    return re.sub(r'\s+',' ',s)
cands={}  # code -> {name, category, country, page}
def add(code, name, cat, country, page):
    code=code.strip()
    if len(code)<20 or len(code)>24: return
    if code in union: return
    name=clean(name)
    if not name: return
    if code not in cands:
        cands[code]={'name':name,'cat':cat,'country':country,'page':page}
    elif len(name)>len(cands[code]['name']):
        cands[code]['name']=name

# ---------- 1. whatsgroup.in ----------
pages=set()
for u in ['https://www.whatsgroup.in/','https://www.whatsgroup.in/whatsapp-groups-category/']:
    try:
        r=fetch(u); print('WGIN',u,r.status_code,len(r.text))
        for l in re.findall(r'href="(https://www\.whatsgroup\.in/[a-z0-9\-/]+)"', r.text):
            if any(x in l for x in ['feed','wp-content','wp-json','xmlrpc','telegram-group']): continue
            pages.add(l.rstrip('/'))
    except Exception as e: print('WGIN err',u,e)
print('whatsgroup.in pages:',len(pages))
CATMAP={'bgmi':'Gaming','free-fire':'Gaming','clash-of-clans':'Gaming','boys':'Friendship','girl':'Friendship','buy-and-sell':'Buy & Sell','online-shopping':'Buy & Sell','hr-jobs':'Jobs','forex-trading':'Finance','html-css':'Technology','indian':'Community & Social','lyrics':'Entertainment','newspaper':'News','puzzles':'Funny','tamil':'Entertainment','tamil-aunty':'Entertainment','video-editors':'Technology','youtube':'Entertainment','dubai':'Community & Social'}
for p in sorted(pages):
    slug=p.rstrip('/').split('/')[-1]
    cat='Community & Social'
    for k,v in CATMAP.items():
        if k in slug: cat=v; break
    country='IN' if 'indian' in slug or 'tamil' in slug else ('AE' if 'dubai' in slug else 'International')
    try:
        r=fetch(p+'/'); time.sleep(0.3)
        rows=re.findall(r'<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text, re.S)
        for name,code in rows: add(code,name,cat,country,p)
        print(f'  {slug}: rows={len(rows)} total_fresh={len(cands)}')
    except Exception as e: print('  err',p,e)
print('after whatsgroup.in fresh:',len(cands))

# ---------- 2. grouplinkshare Bangladesh ----------
bd_pages=['https://grouplinkshare.com/bangladesh-whatsapp-group-links/']
try:
    r=fetch(bd_pages[0]); print('GLS-BD',r.status_code,len(r.text))
    for l in sorted(set(re.findall(r'href="(https://grouplinkshare\.com/[^"]+)"', r.text))):
        if 'bangladesh' in l.lower() or 'bangla' in l.lower(): bd_pages.append(l)
    print('bd pages:',bd_pages)
    for p in sorted(set(bd_pages)):
        try:
            r=fetch(p); time.sleep(0.3)
            rows=re.findall(r'<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text, re.S)
            if not rows:
                codes=re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text)
                print(f'  GLS {p}: no table rows, raw codes={len(set(codes))}')
                continue
            for name,code in rows: add(code,name,'Community & Social','BD',p)
            print(f'  GLS {p}: rows={len(rows)} total_fresh={len(cands)}')
        except Exception as e: print('  GLS err',p,e)
except Exception as e: print('GLS err',e)
print('after grouplinkshare-BD fresh:',len(cands))

# ---------- 3. wtgrouplinks ----------
try:
    r=fetch('https://wtgrouplinks.com/'); print('WTG home',r.status_code,len(r.text))
    wt_pages=set(re.findall(r'href="(https://wtgrouplinks\.com/[^"]+)"', r.text))
    wt_pages={l.rstrip('/') for l in wt_pages if 'whatsapp-group-link' in l and 'feed' not in l}
    print('wtg pages:',len(wt_pages))
    for p in sorted(wt_pages):
        slug=p.rstrip('/').split('/')[-1]
        cat='Community & Social'
        if 'education' in slug: cat='Education'
        elif 'job' in slug: cat='Jobs'
        elif 'news' in slug: cat='News'
        try:
            r=fetch(p+'/'); time.sleep(0.3)
            rows=re.findall(r'<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text, re.S)
            if not rows:
                # try name in same row via different structure
                rows2=re.findall(r'>([^<>]{2,60})<[^>]*>.*?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text, re.S)
                rows=rows2
            for name,code in rows: add(code,name,cat,'IN',p)
            print(f'  WTG {slug}: rows={len(rows)} total_fresh={len(cands)}')
        except Exception as e: print('  WTG err',p,e)
except Exception as e: print('WTG err',e)
print('after wtgrouplinks fresh:',len(cands))
json.dump(cands, open(WAVE+'team17-scratch-cands.json','w'), ensure_ascii=False, indent=1)
print('SAVED', len(cands))
