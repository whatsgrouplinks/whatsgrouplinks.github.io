#!/usr/bin/env python3
"""Team 06 finalize: build the 3 output files from the verify checkpoint + new leads.
- verified: schema {name, category, country, description, invite, image}
- pending: same + reason=transport
- leads: {url, source} for NEW appgrouplink listing pages (Philippines excluded:
  Philippines slices are a retired/exhausted source per task rule 5).
Dedupes verified against itself; validates categories/countries; writes with retries."""
import json, re, time
from pathlib import Path

BASE = Path('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
VALID_CATS = {'Education', 'Jobs', 'Entertainment', 'Islamic', 'News', 'Sports', 'Technology',
              'Health', 'Business', 'Gaming', 'Friendship', 'Community & Social', 'Online Earning',
              'Crypto', 'Cooking', 'Poetry', 'Travel', 'Scholarship', 'Freelance', 'Real Estate',
              'Buy & Sell', 'Finance', 'Funny'}

def write_retry(path, obj):
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    for attempt in range(5):
        try:
            path.write_text(txt, encoding='utf-8')
            # verify read-back
            json.loads(path.read_text(encoding='utf-8'))
            print(f'wrote {path.name}: {len(obj)} records ({len(txt)} bytes)')
            return
        except Exception as e:
            print(f'write attempt {attempt+1} failed for {path.name}: {e}')
            time.sleep(3)
    raise IOError(f'could not write {path}')

chk = json.load(open(BASE / 'team06-scratch-verify.json'))
verified, pending = chk['verified'], chk['pending']
print(f"checkpoint: verified={len(verified)} pending={len(pending)} dead={chk['dead']} "
      f"blocked_live={chk['blocked_live']} channels={chk['channels']}")

PORN_TOKENS = ['bokep', 'bokeh', 'xnxx', 'xvideos', 'pornhub', 'xhamster', 'redtube',
               'onlyfans', 'camgirl', 'porn', 'xxx', 'nude', 'escort', 'call girl',
               'sex video', 'leaked video', 'mms video']
# clean + dedupe verified by invite code
seen, out_v = set(), []
for r in verified:
    if any(t in r['name'].lower() for t in PORN_TOKENS):
        print('FINALIZE-DROP porn:', r['name'][:60])
        continue
    code = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{22})', r['invite'])
    if not code or code.group(1) in seen:
        continue
    seen.add(code.group(1))
    assert r['category'] in VALID_CATS, r
    assert re.fullmatch(r'[A-Z]{2}|International', r['country']), r
    assert r['name'] and r['description'] and r['image'] == ''
    out_v.append(r)
# pending: same checks, keep reason
seen_p, out_p = set(), []
for r in pending:
    code = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{22})', r['invite'])
    if not code or code.group(1) in seen_p:
        continue
    seen_p.add(code.group(1))
    assert r.get('reason') == 'transport'
    out_p.append(r)

new_leads = json.load(open(BASE / 'team06-scratch-newleads.json'))
leads = [{'url': u, 'source': 'appgrouplink related links'}
         for u in sorted(new_leads) if 'philippines' not in u]
print(f'new leads: {len(new_leads)} found, {len(leads)} kept (philippines excluded)')

write_retry(BASE / 'team06-leads-harvest-f.json', out_v)
write_retry(BASE / 'team06-leads-harvest-f-pending.json', out_p)
write_retry(BASE / 'team06-leads-harvest-f-leads.json', leads)
print('FINALIZE DONE')
