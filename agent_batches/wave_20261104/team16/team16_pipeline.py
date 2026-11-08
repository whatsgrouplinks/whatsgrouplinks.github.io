"""TEAM16: groupwhat.com listing re-scrape pipeline. Parse -> filter -> dedupe -> verify."""
import re, json, glob, html, time, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104'
TDIR = WAVE + '/team16'
BS = chr(92); q = BS + '"'; PH = 'ZXQZXQ'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}

ISO = {'Global': 'International', 'India': 'IN', 'Pakistan': 'PK', 'Spain': 'ES',
       'United States': 'US', 'Ghana': 'GH', 'Egypt': 'EG', 'Morocco': 'MA'}
CATMAP = {'Animation': 'Entertainment', 'Business': 'Business', 'Cryptocurrency': 'Crypto',
          'Earning': 'Finance', 'Education': 'Education', 'Finance': 'Finance',
          'Football': 'Sports', 'Friendship': 'Friendship', 'Gaming': 'Gaming',
          'Movies': 'Movies', 'Uncategorized': 'Other'}

PORN_WORDS = ['porn', 'pornhub', 'xxx', 'nude', 'sex video', 'escort', 'call girl',
              'fuck', 'dick', 'pussy', 'boobs', 'anal', 'bokep']
PORN_EMOJI = ['\U0001f975', '\U0001f346', '\U0001f351', '\U0001f51e', '\U0001f4a6',
              '\U0001f445', '\U0001f444', '\U0001f48b']
SCAM_WORDS = ['satta', 'matka', 'hyip', 'money double', 'double your money',
              'paypal receiver', 'loader', 'carding', 'cvv', 'dumps']

def parse_at(h, start):
    i = start; depth = 0; n = len(h)
    while i < n:
        c = h[i]
        if c == BS: i += 2; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                raw = h[start:i+1]
                s = raw.replace(BS+BS+q, PH).replace(q, '"').replace(PH, BS+'"')
                return json.loads(s)
        i += 1
    return None

def recs_of(path):
    h = open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(re.escape('{'+q+'id'+q+':'), h):
        if m.start() > 0 and h[m.start()-1] == ':': continue
        try: obj = parse_at(h, m.start())
        except Exception: continue
        if isinstance(obj, dict) and obj.get('invite_link'): out.append(obj)
    return out

def main():
    union = set(json.load(open(WAVE + '/dedupe_union.json')))
    print('union size:', len(union), flush=True)
    seen = set(); cands = []; drops = Counter()
    fresh = {}
    for f in sorted(glob.glob(TDIR + '/_cat_*.html')):
        cat_slug = re.search(r'_cat_(.+)\.html', f).group(1)
        rs = recs_of(f)
        latest = rs[0].get('updated_at', '') if rs else ''
        fresh[cat_slug] = {'count': len(rs), 'latest_updated': latest,
                           'latest_name': (rs[0].get('name') or '') if rs else ''}
        for r in rs:
            inv = (r.get('invite_link') or '').strip()
            if 'whatsapp.com/channel/' in inv:
                drops['channel'] += 1; continue
            m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})(?:[?/#]|$)', inv)
            if not m:
                drops['bad_code'] += 1; continue
            code = m.group(1)
            if code in union or code in seen:
                drops['dupe'] += 1; continue
            seen.add(code)
            name = html.unescape((r.get('name') or '').strip())
            desc = html.unescape((r.get('description') or '').strip())
            blob = (name + ' ' + desc).lower()
            if any(w in blob for w in PORN_WORDS) or any(e in blob for e in PORN_EMOJI):
                drops['porn'] += 1; continue
            if any(w in blob for w in SCAM_WORDS):
                drops['scam'] += 1; continue
            cands.append({'code': code, 'rec': r, 'cat_slug': cat_slug})
    print('candidates:', len(cands), 'drops:', dict(drops), flush=True)
    json.dump(cands, open(TDIR + '/_t16_cands.json', 'w'), ensure_ascii=False)
    json.dump(fresh, open(TDIR + '/_t16_fresh.json', 'w'), indent=1)
    for k, v in sorted(fresh.items()):
        print('FRESH', k, v['count'], v['latest_updated'], v['latest_name'][:50], flush=True)

if __name__ == '__main__':
    main()
