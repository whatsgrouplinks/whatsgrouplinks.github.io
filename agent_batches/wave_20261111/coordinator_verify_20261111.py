#!/usr/bin/env python3
"""Wave 20261111 coordinator spot verification.
Slow sequential curl-equivalent via one persistent requests.Session (keep-alive:
this VM charges ~25-30s per FRESH TLS connection; warm requests are ~1s).
35-code stratified sample of the repaired clean set + 2 controls + 5
schema-error codes (name recovery attempt: og:title becomes the name).
LIVE = HTTP 200 + non-empty og:title. og:title is also screened for scam/porn.
"""
import json, re, time, random, requests, os

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
OG1 = re.compile(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', re.I)
OG2 = re.compile(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', re.I)
SCAM = re.compile(r'b-?love|forsage|shey[iy]|holiverse|meta[\s\-]?whale|airdrop|binary option|carding', re.I)
PORN = re.compile(r'porn|xxx|xnxx|sex|sexy|hookup|escort|call\s?girl|bokep|nude|naked|erotic|onlyfans|pornhub|brazzers|hentai|18\+|🔞', re.I)

clean = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_clean.json')))
teams = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_clean_teams.json')))

# flagged items (must be in the sample)
FLAGGED = ['DrtWGFG6BUtI8jm9tX0NIl',   # GLOBAL WEB 3 (team23, KYC bullet)
           'I8qdaU3ukaOGXOM5lFvkxY',   # Weltrade/Deriv signals (team20)
           'FFMautp0NOzIQu9JwFLb2C',   # Teen Patti blue (team14)
           'IczPBaqiprmD3Wb6tCCbHt',   # '.' degenerate name (team12)
           'L0z8mtqCPV0CkfZnw76Iec',   # تداول أموال money-trading (team26)
           'DVfeJFbzz3bKkgP6ypIEyp',   # earn-money-daily pitch (team26)
           'BIc5wPBCqTEIGykHNmHBVC',   # Adfly (team26)
           'FeB3NezgPxRK3SDXSc7Qjt',   # restored: Compra e venda e rolo
           'F9ERzi3KAWS831WI3zetmC',   # restored: sexta-Friday false positive
           'KIHOLHORne3BFwzTMJAYd1',   # restored: pet adoption
           'FeCmIEiMupt8ahCwcW71Ee',   # restored: 18+ age-gate friendship
           'LF8XXj85F4rA7EQBP0af7R']   # restored: hookah age gate
pool = [c for c in clean if c['invite'].rsplit('/', 1)[-1] not in FLAGGED]
random.seed(20261111)
sample = [next(c for c in clean if c['invite'].rsplit('/', 1)[-1] == code) for code in FLAGGED]
sample += random.sample(pool, 35 - len(FLAGGED))

SCHEMA_CODES = ['CxbB7KGXrnZ5qCMzJzL6mk', 'DLGjETM8O1iGeNSDJJoAnU', 'DnncEuOYpy9FHj9CtJo7zF',
                'HEd8YypmDP79JFDbMupwuS', 'LQsFNeDaq9W03ptXrgHcaK']
CONTROLS = [('live', 'IZVRL7Hy2JW8hntMEB9WUJ'), ('fake', 'ZZZZZZZZZZZZZZZZZZZZZZ')]

s = requests.Session()
s.headers.update({'User-Agent': UA})

def check(code):
    url = f'https://chat.whatsapp.com/{code}'
    for attempt in (1, 2):
        try:
            r = s.get(url, timeout=90, allow_redirects=True)
            body = r.text
            m = OG1.search(body) or OG2.search(body)
            og = (m.group(1).strip() if m else '')
            if r.status_code == 200 and og:
                return {'code': code, 'status': 'live', 'http': 200, 'og_title': og, 'attempt': attempt}
            if r.status_code == 200 and not og:
                if attempt == 1:
                    time.sleep(6)
                    continue
                return {'code': code, 'status': 'dead', 'http': 200, 'og_title': '', 'attempt': attempt}
            return {'code': code, 'status': 'pending', 'http': r.status_code, 'og_title': og, 'attempt': attempt}
        except Exception as e:
            if attempt == 1:
                time.sleep(6)
                continue
            return {'code': code, 'status': 'pending', 'http': 0, 'og_title': '', 'reason': str(e)[:120], 'attempt': attempt}
    return {'code': code, 'status': 'pending', 'http': 0, 'og_title': ''}

results = []
for it in sample:
    code = it['invite'].rsplit('/', 1)[-1]
    r = check(code)
    r['banked_name'] = it['name']
    r['team'] = teams.get(code)
    r['og_scam'] = bool(SCAM.search(r['og_title'])) if r['og_title'] else False
    r['og_porn'] = bool(PORN.search(r['og_title'])) if r['og_title'] else False
    results.append(r)
    print(f"{code} team{r['team']} {r['status']} og={r['og_title'][:60]!r} scam={r['og_scam']} porn={r['og_porn']}", flush=True)
    time.sleep(1)

controls = []
for kind, code in CONTROLS:
    r = check(code)
    r['kind'] = kind
    controls.append(r)
    print(f"CONTROL {kind} {code} {r['status']} og={r['og_title'][:60]!r}", flush=True)
    time.sleep(1)

schema = []
for code in SCHEMA_CODES:
    r = check(code)
    schema.append(r)
    print(f"SCHEMA {code} {r['status']} og={r['og_title'][:80]!r}", flush=True)
    time.sleep(1)

state = {'sample': results, 'controls': controls, 'schema_codes': schema,
         'live': sum(1 for r in results if r['status'] == 'live'),
         'dead': sum(1 for r in results if r['status'] == 'dead'),
         'pending': sum(1 for r in results if r['status'] == 'pending')}
json.dump(state, open(os.path.join(WAVE_DIR, 'coordinator_verify_state_20261111.json'), 'w'), indent=1, ensure_ascii=False)
print(f"SAMPLE: {state['live']}/35 live, {state['dead']} dead, {state['pending']} pending")
print(f"CONTROLS: live={controls[0]['status']} fake={controls[1]['status']}")
print(f"SCHEMA: {[(r['code'][:6], r['status']) for r in schema]}")
