import json, re, subprocess, time, html, sys

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261030/'
WORK = WAVE + 'team17_work/'

dedupe = set(x.strip() for x in open(WAVE + 'dedupe_union_codes.txt', encoding='utf-8', errors='ignore') if x.strip())
print(f"dedupe loaded: {len(dedupe)}", flush=True)

# merge candidates, prefer qatar names first for Qatar-slice items
cands = {}
for f in ['qatar_items.json', 'emirates_items.json']:
    for d in json.load(open(WORK + f)):
        if d['code'] not in cands:
            cands[d['code']] = d

skipped_dup = [c for c in cands if c in dedupe]
print(f"candidates: {len(cands)}, already in union dedupe: {len(skipped_dup)}", flush=True)

def verify(code):
    url = f"https://chat.whatsapp.com/{code}"
    r = subprocess.run(
        ['curl', '-sL', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
         '-w', '\n%{http_code}\n', '--max-time', '30', url],
        capture_output=True, text=True)
    lines = r.stdout.split('\n')
    http = lines[-2].strip() if len(lines) >= 2 else ''
    body = '\n'.join(lines[:-2])
    m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', body, re.I)
    title = html.unescape(m.group(1)).strip() if m else ''
    dead = ('couldn' in title.lower() and 'look up' in title.lower()) or not title or http != '200'
    return http, title, dead

live, dead, uncertain = [], [], []
todo = [c for c in cands if c not in dedupe]
for i, code in enumerate(todo):
    http, title, isdead = verify(code)
    status = 'DEAD' if isdead else 'LIVE'
    print(f"[{i+1}/{len(todo)}] {code} {status} http={http} og:title={title[:60]}", flush=True)
    rec = {'code': code, 'name': cands[code]['name'], 'http': http, 'og_title': title}
    if isdead:
        dead.append(rec)
    else:
        live.append(rec)
    time.sleep(0.5)

json.dump({'live': live, 'dead': dead, 'skipped_dup': skipped_dup}, open(WORK + 'verify_results.json', 'w'), ensure_ascii=False, indent=1)
print(f"\nLIVE={len(live)} DEAD={len(dead)} SKIPPED_DUP={len(skipped_dup)}", flush=True)
