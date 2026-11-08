#!/usr/bin/env python3
"""team36: retry-verify Nov-3 misc small pending files. Verified -> team36-pending-retry.json,
still-failing -> team36-unverified-pending.json. Working dir: wave_20261104/."""
import json, re, html, time, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter

WAVE3 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/'
WAVE4 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
def eprint(*a, **k):
    k.setdefault('file', sys.stderr)
    k.setdefault('flush', True)
    print(*a, **k)

CODE_RE = re.compile(r'^[A-Za-z0-9]{20,24}$')
INVITE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OG_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)

ALLOWED_CATS = {"Sports","Gaming","Jobs","Education","Entertainment","Friendship","News",
    "Islamic","Business","Finance","Buy-Sell","Health","Community","Technology","Crypto",
    "Travel","Music","Movies","Food","Pets","Funny","Girls","Regional","Other"}

PORN_PAT = re.compile(r'(pornhub|\bporn\b|\bxxx\b|\bnude(s)?\b|sex\s*video|\bescort\b|call\s*girl|\bfuck\b|\bdick\b|\bpussy\b|\bboobs\b|\banal\b|\bbokep\b|مزا\s*دینے|مزہ\s*دینے|🥵|🍆|🍑|🔞|💦|👅|👄|💋|18\+\s*(sex|porn|adult|nude)|sex\s*18\+)', re.I)
SCAM_PAT = re.compile(r'(satta|hyip|paypal\s*receiver|money\s*mule|loader\s*account|double\s*your\s*money|guaranteed\s*returns|forex\s*doubler|click\s*the\s*link\s*to\s*claim)', re.I)
MINORS_PAT = re.compile(r'(under\s*18|teen\s*(dating|love|girls?)|school\s*(girl|kid)s?\s*(dating|love)|minor)', re.I)

# ---------- load union ----------
union = set(json.load(open(WAVE4 + 'dedupe_union.json')))
eprint(f'union loaded: {len(union)} codes', flush=True)

CATMAP = {
    'online-shopping': 'Buy-Sell',
    'sports-and-fitness': 'Sports',
    'jobs': 'Jobs', 'education': 'Education', 'entertainment': 'Entertainment',
    'gaming': 'Gaming', 'business': 'Business', 'finance': 'Finance', 'money': 'Finance',
    'marketing': 'Business', 'news': 'News', 'islamic': 'Islamic', 'health': 'Health',
    'community': 'Community', 'technology': 'Technology', 'crypto': 'Crypto',
    'travel': 'Travel', 'music': 'Music', 'movies': 'Movies', 'food': 'Food',
    'pets': 'Pets', 'funny': 'Funny', 'girls': 'Girls', 'friendship': 'Friendship',
    'regional': 'Regional', 'sports': 'Sports',
}
def map_cat(s):
    if not s: return 'Other'
    s2 = str(s).strip().lower().replace('_','-').replace(' ','-')
    for k,v in CATMAP.items():
        if k in s2: return v
    cap = str(s).strip().title()
    return cap if cap in ALLOWED_CATS else 'Other'

def clean_title(t):
    if not t: return ''
    t = html.unescape(t).strip()
    t = re.sub(r'\s+', ' ', t)
    return t

def is_generic(t):
    return t.lower().strip() in ('join now','click here','whatsapp group','whatsapp group link',
        'join group','join whatsapp group','group link','join','whatsapp') or len(t.strip()) < 3

DESC_TPL = {
 'Buy-Sell': 'An active buy-sell WhatsApp group for online shopping deals and marketplace offers. Members share product listings, prices and stock updates daily.',
 'Sports': 'An active sports WhatsApp group for fans and players to chat, share match updates and connect with fellow sports lovers.',
 'Jobs': 'An active jobs WhatsApp group sharing job openings, career tips and hiring updates. Members connect over employment opportunities and professional growth.',
 'Gaming': 'An active gaming WhatsApp community for players to chat, share tips, squad up and stay updated on the latest games and events.',
 'Education': 'An active education WhatsApp group for students and learners to share study notes, exam updates and learning resources.',
 'Entertainment': 'An active entertainment WhatsApp group for fun chats, trending topics, memes and the latest buzz with fellow members.',
 'News': 'An active news WhatsApp group sharing the latest headlines, updates and discussions with members every day.',
 'Community': 'An active community WhatsApp group where members chat, share updates and connect with like-minded people.',
 'Business': 'An active business WhatsApp group for entrepreneurs and professionals to network, share ideas and discuss market trends.',
 'Finance': 'An active finance WhatsApp group sharing money tips, market updates and earning discussions with members.',
 'Crypto': 'An active crypto WhatsApp group for discussing digital currencies, market trends and trading insights with members.',
 'Other': 'An active WhatsApp group where members chat, share updates and connect with like-minded people.',
}
def make_desc(name, cat, country):
    base = DESC_TPL.get(cat, DESC_TPL['Other'])
    cw = '' if country in ('International', None) else f' in {country}'
    return f'{name} is {base} A lively{cw} community for daily conversation and updates.'.replace('  ',' ')

def porn_drop(reason, title, ctx):
    eprint(f'  PORN-DROP [{reason}] {ctx}: {title[:80]}', flush=True)

# ---------- collect candidates ----------
# file -> builder
raw_items = []   # (code, src_title, cat, src_file) from raw formats
full_items = []  # dicts with name/category/country/description/invite
seen = set()
def add_candidate(code, src_file, name=None, title=None, category=None, country=None, description=None):
    code = (code or '').strip()
    if not CODE_RE.match(code): return 'bad-code'
    if code in union or code in seen: return 'dup'
    seen.add(code)
    if name and category and description:
        full_items.append({'code': code, 'name': name, 'category': category, 'country': country or 'International',
                           'description': description, 'file': src_file})
    else:
        raw_items.append({'code': code, 'title': title or '', 'category': category, 'file': src_file})
    return 'ok'

stats = {'files': {}, 'bad-code': 0, 'dup': 0}
def ingest(path, src):
    try:
        d = json.load(open(WAVE3 + path))
    except Exception as e:
        eprint(f'{src}: load error {e}', flush=True); return
    n = 0
    if isinstance(d, dict): d = d.get('items', d.get('groups', []))
    for x in d:
        n += 1
        if isinstance(x, list):  # team18-style arrays: [title, code, country, tag]
            r = add_candidate(x[1] if len(x) > 1 else '', src, title=x[0] if x else '')
        elif isinstance(x, dict):
            code = x.get('code')
            if not code and x.get('invite'):
                m = INVITE_RE.search(x['invite']); code = m.group(1) if m else ''
            name = x.get('name'); title = x.get('title') or x.get('post_title')
            cat = x.get('category') or map_cat(x.get('category_slug') or x.get('cat'))
            if name and cat and x.get('description'):
                r = add_candidate(code, src, name=name, category=cat,
                                  country=x.get('country') or 'International',
                                  description=x.get('description'))
            else:
                r = add_candidate(code, src, title=title, category=cat)
        else:
            r = 'bad-code'
        if r in stats: stats[r] += 1
    stats['files'][src] = n
    eprint(f'{src}: {n} rows ingested', flush=True)

# explicit slice
for f in ['team30-unverified-pending.json', 'team10-unverified-pending.json',
          'team11-unverified-pending.json', 'team11b-unverified-pending.json',
          'team12-unverified-pending.json', 'team28b-unverified-pending.json',
          'team29-unverified-pending.json', 'team46-unverified-pending.json',
          'team36-unverified-pending.json']:
    ingest(f, f)
eprint(f'total candidates: full={len(full_items)} raw={len(raw_items)}', flush=True)
eprint(f'skipped bad-code={stats["bad-code"]} dup-vs-union={stats["dup"]}', flush=True)

# ---------- verify ----------
def make_session():
    s = requests.Session()
    s.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    ad = HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=1)
    s.mount('https://', ad); s.mount('http://', ad)
    return s

def og_title(code):
    # returns ('ok', title) | ('transport', err) | ('rate-limited', '')
    # rebuilds the shared session on transport error and retries once (brief: rebuild session on error)
    global sess
    try:
        r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=50, allow_redirects=True)
    except Exception as e:
        try:
            sess.close()
        except Exception:
            pass
        sess = make_session()
        time.sleep(1)
        try:
            r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=50, allow_redirects=True)
        except Exception as e2:
            return ('transport', str(e2)[:80])
    if r.status_code == 429:
        return ('rate-limited', '')
    if r.status_code >= 500:
        return ('transport', f'HTTP {r.status_code}')
    m = OG_RE.search(r.text) or OG_RE2.search(r.text)
    title = clean_title(m.group(1)) if m else ''
    return ('ok', title)

verified, pending, leads = [], [], []
porn_drops = 0
rate_limited_hit = False
checked = 0

def atomic_write(path, obj):
    tmp = path + '.tmp'
    for attempt in range(4):
        try:
            with open(tmp, 'w') as f:
                json.dump(obj, f, ensure_ascii=False, indent=1)
                f.flush()
            os.replace(tmp, path)
            return True
        except PermissionError as e:
            eprint(f'  write attempt {attempt+1} failed ({e}) — retrying', flush=True)
            time.sleep(3)
    eprint(f'  FATAL: could not write {path}', flush=True)
    return False

def checkpoint(kind, i, code, outcome, payload):
    ck = {'kind': kind, 'idx': i, 'code': code, 'outcome': outcome, 'payload': payload}
    with open(WAVE4 + 'team36_verify_ckpt.jsonl', 'a') as f:
        f.write(json.dumps(ck, ensure_ascii=False) + '\n')

all_cands = [('full', i) for i in range(len(full_items))] + [('raw', i) for i in range(len(raw_items))]
# fresh checkpoint for this run
eprint(f'verifying {len(all_cands)} codes with 24 workers...', flush=True)
t0 = time.time()
sess = make_session()
with ThreadPoolExecutor(max_workers=24) as ex:
    futs = {}
    def submit(kind, i):
        code = full_items[i]['code'] if kind == 'full' else raw_items[i]['code']
        futs[ex.submit(og_title, code)] = (kind, i, code)
    for kind, i in all_cands:
        submit(kind, i)
    for fut in as_completed(futs):
        kind, i, code = futs[fut]
        checked += 1
        try:
            status, title = fut.result()
        except Exception as e:
            status, title = 'transport', str(e)[:80]
        if status == 'rate-limited':
            rate_limited_hit = True
            print('RATE LIMITED (429) — stopping verification', flush=True)
            break
        if status == 'transport':
            entry = {'code': code, 'note': f'transport failure — {title}'}
            if kind == 'full':
                f = full_items[i]
                entry.update({'name': f['name'], 'category': f['category'], 'country': f['country'],
                              'description': f['description'], 'invite': f'https://chat.whatsapp.com/{code}',
                              'image': '', 'file': f['file']})
            else:
                r0 = raw_items[i]
                entry.update({'title': r0['title'], 'category': r0['category'], 'file': r0['file']})
            pending.append(entry)
            continue
        # status ok
        if not title:
            continue  # dead link — skip silently
        if PORN_PAT.search(title):
            porn_drops += 1; porn_drop('og:title', title, code)
            continue
        if SCAM_PAT.search(title):
            porn_drops += 1; porn_drop('scam', title, code)
            continue
        if MINORS_PAT.search(title):
            lead = {'domain': 'chat.whatsapp.com', 'url': f'https://chat.whatsapp.com/{code}',
                    'why': f'minors-targeted per og:title "{title[:60]}" — excluded, do not verify'}
            leads.append(lead)
            continue
        if kind == 'full':
            f = full_items[i]
            name = f['name']
            desc = f['description']
            if is_generic(name) or len(name) > 120:
                name = title
            if 'Pending verification' in desc or is_generic(f['name']):
                desc = make_desc(name, f['category'], f['country'])
            item = {'name': name, 'category': f['category'], 'country': f['country'],
                    'description': desc, 'invite': f'https://chat.whatsapp.com/{code}', 'image': ''}
            verified.append(item)
        else:
            r0 = raw_items[i]
            if PORN_PAT.search(r0['title'] or ''):
                porn_drops += 1; porn_drop('src-title', r0['title'], code)
                continue
            item = {'name': title, 'category': r0['category'], 'country': 'International',
                    'description': make_desc(title, r0['category'], 'International'),
                    'invite': f'https://chat.whatsapp.com/{code}', 'image': ''}
            verified.append(item)
        if checked % 50 == 0:
            eprint(f'  checked {checked}/{len(all_cands)} — verified {len(verified)} pending {len(pending)} ({time.time()-t0:.0f}s)', flush=True)

elapsed = time.time() - t0
eprint(f'done: checked={checked} verified={len(verified)} pending={len(pending)} porn_drops={porn_drops} elapsed={elapsed:.0f}s', flush=True)

# if rate-limited, bank everything not yet checked as pending rate-limited
if rate_limited_hit:
    done_keys = set()
    # rebuild set of (kind,i) processed: simpler — re-walk futures in submission order
    # approximate: mark all remaining futures as rate-limited pending
    for fut, (kind, i, code) in futs.items():
        if not fut.done():
            fut.cancel()
            entry = {'code': code, 'note': 'rate-limited (HTTP 429 during verify) — resume next wave'}
            if kind == 'full':
                f = full_items[i]
                entry.update({'name': f['name'], 'category': f['category'], 'country': f['country'],
                              'description': f['description'], 'invite': f'https://chat.whatsapp.com/{code}',
                              'image': '', 'file': f['file']})
            else:
                r0 = raw_items[i]
                entry.update({'title': r0['title'], 'category': r0['category'], 'file': r0['file']})
            pending.append(entry)
    leads.append({'domain': 'chat.whatsapp.com', 'url': 'https://chat.whatsapp.com/<code>',
                  'why': f'HTTP 429 hit at checked={checked}; resume team36 retry from remaining pending codes'})

result = {'verified': verified, 'pending': pending, 'leads': leads,
          'summary': {'verified': len(verified), 'pending': len(pending), 'leads': len(leads),
                      'porn_drops': porn_drops, 'rate_limited': rate_limited_hit, 'checked': checked,
                      'files': stats['files'], 'bad_code': stats['bad-code'], 'dup': stats['dup']}}
print(json.dumps(result, ensure_ascii=False))
eprint(f'DONE verified={len(verified)} pending={len(pending)} leads={len(leads)} porn_drops={porn_drops}')
eprint(json.dumps({'files': stats['files'], 'bad_code': stats['bad-code'], 'dup': stats['dup'],
                  'verified': len(verified), 'pending': len(pending), 'leads': len(leads),
                  'porn_drops': porn_drops, 'rate_limited': rate_limited_hit, 'checked': checked}, indent=1))
