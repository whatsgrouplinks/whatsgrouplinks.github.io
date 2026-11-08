import requests, re, time, html as H, json, sys
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36'
def log(*a): print(*a, file=sys.stderr, flush=True)
def fetch(url, minlen=50000):
    for i in range(12):
        try:
            s=requests.Session(); s.headers.update({'User-Agent':UA})
            r=s.get(url,timeout=60); t=r.text
            if len(t) >= minlen: return t
            log(f'fetch try{i} SHORT len={len(t)}')
        except Exception as e:
            log(f'fetch try{i} {type(e).__name__}'); time.sleep(4+i*2)
    return None
home=fetch('https://whatgroups.com/')
fx=fetch('https://whatgroups.com/forex-trading-whatsapp-group-links/')
if not home or not fx:
    log('FETCH FAILED'); sys.exit(1)
log('lens',len(home),len(fx))
cands=[]
for t in re.findall(r'<tr[^>]*>(.*?)</tr>', home, re.S):
    m=re.search(r'href="(https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24}))"', t)
    if not m: continue
    nm=H.unescape(re.sub(r'<[^>]+>',' ',t)); nm=re.sub(r'\s+',' ',nm).strip()
    nm=re.sub(r'\s*Link\s*$','',nm).strip()
    if nm: cands.append((nm, m.group(2), 'home'))
for m in re.finditer(r'<td[^>]*>\s*(.*?)\s*</td>\s*<td[^>]*>\s*(?:<strong>)?<a[^>]*href="(https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24}))"', home, re.S):
    nm=H.unescape(re.sub(r'<[^>]+>',' ',m.group(1))); nm=re.sub(r'\s+',' ',nm).strip()
    if nm: cands.append((nm, m.group(3), 'home'))
for t in re.findall(r'<tr[^>]*>(.*?)</tr>', fx, re.S):
    m=re.search(r'href="(https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24}))"', t)
    if not m: continue
    nm=H.unescape(re.sub(r'<[^>]+>',' ',t)); nm=re.sub(r'\s+',' ',nm).strip()
    nm=re.sub(r'\s*Link\s*$','',nm).strip()
    if nm: cands.append((nm, m.group(2), 'forex'))
log('raw cands', len(cands))
heads=[(m.start(), H.unescape(re.sub('<[^>]+>','',m.group(1))).strip()) for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', home, re.S)]
def section_of(name):
    pos=home.find(name[:25]); h=''
    for p,hh in heads:
        if p<pos: h=hh
        else: break
    return h
def keep_home(nm, code):
    sec=section_of(nm); nl=nm.lower()
    if 'Online Earning' in sec: return True
    if 'Pakistan' in sec and any(k in nl for k in ['earning','forex','crypto','trading','trader','freelanc']): return True
    if 'USA' in sec and any(k in nl for k in ['earning','income','forex','crypto','trading']): return True
    if 'Sri Lanka' in sec and any(k in nl for k in ['earning','crypto','forex','trading']): return True
    if 'Tamil' in sec and 'earning' in nl: return True
    return False
filtered=[(nm,code,src) for nm,code,src in cands if (src=='forex' or keep_home(nm,code))]
log('filtered', len(filtered))
SCAM_NAMES={'binance 100% profit','colour trading high profit','big daddy prediction','security deposits','forex account manager'}
scam=[c for c in filtered if c[0].lower() in SCAM_NAMES]
ok=[c for c in filtered if c[0].lower() not in SCAM_NAMES]
log('scam drops:',len(scam),[s[0] for s in scam])
seen={}; uniq=[]
for nm,code,src in ok:
    if code in seen: continue
    seen[code]=nm; uniq.append((nm,code,src))
log('uniq',len(uniq))
union=set(json.load(open('dedupe_union.json')))
fresh=[c for c in uniq if c[1] not in union]
log('fresh after union:',len(fresh),'| already in union:',len(uniq)-len(fresh))
vs=requests.Session(); vs.headers.update({'User-Agent':UA})
verified=[]; pending=[]; dead=0
for i,(nm,code,src) in enumerate(fresh):
    title=''; terr=None
    for att in range(3):
        try:
            r=vs.get('https://chat.whatsapp.com/'+code, timeout=50)
            if r.status_code==429:
                terr='rate-limited'; break
            m=re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
            title=H.unescape(m.group(1)).strip() if m else ''
            break
        except Exception as e:
            terr=type(e).__name__; time.sleep(2+att*2)
    if terr=='rate-limited':
        pending.append([nm,code,'rate-limited'])
        for nm2,code2,src2 in fresh[i+1:]:
            pending.append([nm2,code2,'rate-limited (batch stop)'])
        log('RATE LIMITED at',i); break
    if title: verified.append([nm,code,title])
    elif terr: pending.append([nm,code,'transport failure: '+terr])
    else: dead+=1
    if i%20==0: log(f'progress {i}/{len(fresh)} verified={len(verified)} pending={len(pending)} dead={dead}')
log(f'DONE verified={len(verified)} pending={len(pending)} dead={dead}')
json.dump({'verified':verified,'pending':pending,'dead':dead,'scam':[[s[0],s[1]] for s in scam]}, sys.stdout)
