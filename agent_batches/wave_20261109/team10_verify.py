import json, re, subprocess, html, time
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

existing = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
raw = json.load(open(WAVE + 'team10_raw.json'))

# code -> best record (first page in batch order wins)
recs = {}
for r in raw:
    for c in r.get('codes', []):
        if c not in recs:
            recs[c] = r
fresh = {c: r for c, r in recs.items() if c not in existing}
print('distinct codes:', len(recs), '| fresh vs existing:', len(fresh),
      '| already-known:', len(recs) - len(fresh))
json.dump({c: {'url': r['url'], 'title': r['title'], 'desc': r['desc']}
           for c, r in fresh.items()},
          open(WAVE + 'team10_fresh_codes.json', 'w'), ensure_ascii=False, indent=1)

GENERIC = {'whatsapp group', 'join this group on whatsapp', 'whatsapp',
           'join group on whatsapp', 'whatsapp group invite link'}

def og_title(body):
    m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
    if not m:
        m = re.search(r"og:title['\"]?\s*content=['\"]([^'\"]*)", body)
    return html.unescape(m.group(1)).strip() if m else ''

def check(args):
    code, rec = args
    last_err = ''
    for attempt in range(3):
        try:
            p = subprocess.run(['curl', '-s', '-m', '30', '-A', UA,
                                'https://chat.whatsapp.com/' + code],
                               capture_output=True, text=True, timeout=40)
            body = p.stdout or ''
            t = og_title(body)
            if t and t.lower() not in GENERIC:
                return (code, 'live', t, attempt)
            if t and t.lower() in GENERIC:
                return (code, 'dead', t, attempt)  # generic placeholder = dead invite
            # empty og:title -> ambiguous, retry spaced apart
            last_err = 'empty-og-title'
            time.sleep(8)
        except Exception as e:
            last_err = 'transport:' + str(e)[:60]
            time.sleep(5)
    return (code, 'pending' if 'transport' in last_err else 'dead', '', 2)

items = list(fresh.items())
results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for code, st, title, att in ex.map(check, items):
        results[code] = {'status': st, 'og_title': title, 'attempts': att + 1,
                         'url': fresh[code]['url'], 'page_title': fresh[code]['title'],
                         'page_desc': fresh[code]['desc']}
        print(code, st, '|', title[:70], flush=True)
        time.sleep(0.6)

json.dump(results, open(WAVE + 'team10_verify.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(r['status'] for r in results.values()))
print('DONE')
