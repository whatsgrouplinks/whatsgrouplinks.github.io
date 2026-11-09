import json, re, subprocess, time, html, threading
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
DROP_RE = re.compile(r'porn|xxx|sex(y|ual)?|hookup|escort|cam[- ]?girl|camgirl|nude|naked|adult\s*video|b[-\s]?love|forsage|shey?i\b|airdrop|free\s*money|double\s*your\s*money|onlyfans|desi\s*viral\s*video|ننگی|ہاٹ|सविता भाभी|കളിവീട്', re.I)
PROHIB_RE = re.compile(r'[^.!?\n]*(not allowed|prohibit|na\s*karein|don\'?t\s+share|do\s+not\s+share|no\s+porn|no\s+xxx|strictly\s+prohibited|not\s+share|allowed\s+nahi|mana\s+hai)[^.!?\n]*[.!?\n]?', re.I)
PHONE_RE = re.compile(r'\+?\d[\d\s\-()]{7,}\d')
URL_RE = re.compile(r'https?://\S+|www\.\S+')
GENERIC = {'whatsapp group invite','join group','whatsapp','join whatsapp group','whatsapp group'}
pool = {r['code']: r for r in json.load(open('team18_raw/team18_pool.json'))}
results = json.load(open('team18_raw/team18_verify.json'))
print('pool', len(pool), 'verified', len(results), flush=True)

# extra snippet codes (round-2 additions)
extra = {
 'I8rYWk7i6flCAd8Ov9WkcR': {'code':'I8rYWk7i6flCAd8Ov9WkcR','name':'WhatsApp Community','category':'Business','country':'KE','description':'A WhatsApp community for business discussions and updates. Members share updates, discussions and helpful posts.','invite':'https://chat.whatsapp.com/I8rYWk7i6flCAd8Ov9WkcR','src':'search-snippet-flexifunnels'},
 'KFOSZq2EmqAL3CHEv4xdwZ': {'code':'KFOSZq2EmqAL3CHEv4xdwZ','name':'Level Up Women Community','category':'Community & Social','country':'FR','description':'A WhatsApp community for women focused on success, work and personal growth. Members share encouragement, tips and helpful discussions.','invite':'https://chat.whatsapp.com/KFOSZq2EmqAL3CHEv4xdwZ','src':'search-snippet-youtube'},
}
for c, r in extra.items():
    if c not in pool: pool[c] = r

def check(code):
    url = f'https://chat.whatsapp.com/{code}'
    try:
        r = subprocess.run(['curl','-s','-L','--max-time','20','-A',UA,'-w','\n%{http_code}',url],
                           capture_output=True, text=True, timeout=30)
        body = r.stdout or ''
        m = re.search(r'\n(\d{3})\s*$', body)
        http = int(m.group(1)) if m else 0
        body_only = body[:m.start()] if m else body
        og = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', body_only, re.I)
        if not og:
            og = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body_only, re.I)
        return {'code':code,'http':http,'og_title':(og.group(1).strip() if og else ''),'curl_rc':r.returncode}
    except Exception as e:
        return {'code':code,'http':0,'og_title':'','curl_rc':-1,'error':str(e)[:100]}

# retries: 200+empty -> up to 2 more attempts, spaced; extra codes get first check
retry_codes = [c for c, v in results.items() if v.get('http') == 200 and not (v.get('og_title') or '').strip()]
todo_extra = [c for c in extra if c not in results]
print('ambiguous (200+empty) to retry:', len(retry_codes), 'extra to check:', len(todo_extra), flush=True)
lock = threading.Lock(); last = [0.0]
def gated(code):
    with lock:
        gap = 0.6 - (time.time() - last[0])
        if gap > 0: time.sleep(gap)
        last[0] = time.time()
    return check(code)
for rnd in range(2):
    jobs = retry_codes + (todo_extra if rnd == 0 else [])
    if not jobs: break
    print(f'retry round {rnd+1}: {len(jobs)} checks', flush=True)
    from concurrent.futures import as_completed as _ac
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(gated, j): j for j in jobs}
        for _f in _ac(futs):
            res = _f.result()
            c = res['code']
            if c in extra and c not in results:
                results[c] = res
            elif res.get('og_title'):
                results[c] = res
                if c in retry_codes: retry_codes.remove(c)
            else:
                results[c] = res  # keep latest (still empty)
            print(' retry', c, res['http'], repr(res['og_title'][:50]), flush=True)
            json.dump(results, open('team18_raw/team18_verify.json','w'), indent=1)
    if retry_codes and rnd == 0:
        print('spacing 120s before final retry round...', flush=True); time.sleep(120)

# classify
cands, pending, dead, screened_post = [], [], [], []
for code, rec in pool.items():
    v = results.get(code)
    if not v:
        pending.append({'code':code,'invite':rec['invite'],'note':'not checked (verifier did not reach it)','src':rec.get('src')}); continue
    http, og = v.get('http', 0), html.unescape((v.get('og_title') or '').strip())
    og_clean = re.sub(r'\s+', ' ', og).strip()
    if http == 0 or v.get('curl_rc', 0) not in (0,):
        pending.append({'code':code,'invite':rec['invite'],'note':f"transport failure http={http} curl_rc={v.get('curl_rc')} err={v.get('error','')} ",'src':rec.get('src'),'og_title':og_clean}); continue
    if http != 200:
        dead.append({'code':code,'invite':rec['invite'],'http':http,'og_title':og_clean,'src':rec.get('src')}); continue
    if not og_clean or og_clean.lower() in GENERIC:
        dead.append({'code':code,'invite':rec['invite'],'http':http,'og_title':og_clean,'src':rec.get('src'),'note':'200 but og:title empty after retries (ambiguous unresolved)'}); continue
    reason = DROP_RE.search(PROHIB_RE.sub(' ', og_clean + ' ' + (rec.get('description') or '')))
    if reason:
        screened_post.append({'code':code,'invite':rec['invite'],'og_title':og_clean,'reason':'screen:'+reason.group(0),'src':rec.get('src')}); continue
    name = PHONE_RE.sub('', og_clean).strip()
    name = re.sub(r'\s+', ' ', name)[:100].strip()
    if len(re.sub(r'[^\w]', '', name, flags=re.UNICODE)) < 2:
        screened_post.append({'code':code,'invite':rec['invite'],'og_title':og_clean,'reason':'junk og:title','src':rec.get('src')}); continue
    desc = (rec.get('description') or '').strip()
    desc = PHONE_RE.sub('', URL_RE.sub('', desc)).strip()
    desc = re.sub(r'\s+', ' ', desc)
    desc = re.sub(r'(?i)\b(groupssor|groupjoin|wagroupshub|wglfinder|groupsnest|groupwa|grouplinksforyou|techsslash)\b', '', desc).strip()
    if not desc:
        desc = f"A WhatsApp community for {rec['category'].lower()} discussions and updates. Members share updates, discussions and helpful posts."
    sents = re.split(r'(?<=[.!?])\s+', desc)
    desc = ' '.join(sents[:2])[:300]
    cands.append({'name': name, 'category': rec['category'], 'country': rec.get('country') or 'IN',
                  'description': desc, 'invite': f'https://chat.whatsapp.com/{code}'})

print('LIVE candidates:', len(cands), '| pending:', len(pending), '| dead:', len(dead), '| post-screen dropped:', len(screened_post), flush=True)
json.dump(cands, open('team18-candidates.json','w'), indent=1, ensure_ascii=False)
json.dump(pending, open('team18-pending.json','w'), indent=1)
json.dump(dead, open('team18_raw/team18_dead.json','w'), indent=1)
json.dump(screened_post, open('team18_raw/team18_screened_post.json','w'), indent=1)
from collections import Counter
print('cand by cat:', Counter(c['category'] for c in cands))
print('cand by country:', Counter(c['country'] for c in cands).most_common(12))
print('cand by src check done via pool mapping')
