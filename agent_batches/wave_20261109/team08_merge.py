"""Merge pass1 + retry1 + retry2 into final verify set, then build outputs + summary."""
import json, re
from collections import Counter

pass1 = {v['code']: v for v in json.load(open('team08_verify_slice_pass1.json'))}
r1 = {v['code']: v for v in json.load(open('team08_verify_retry1.json'))}
r2 = {}
try:
    r2 = {v['code']: v for v in json.load(open('team08_verify_retry2.json'))}
except FileNotFoundError:
    print('WARNING: retry2 file missing; merging pass1+retry1 only')

final = {}
pending = []
for code, v in pass1.items():
    title = v.get('title', '')
    http = v.get('http', 0)
    attempts = 1
    if code in r1:
        attempts += 1
        if r1[code].get('title'):
            title = r1[code]['title']; http = r1[code]['http']
    if code in r2:
        attempts += 1
        if r2[code].get('title'):
            title = r2[code]['title']; http = r2[code]['http']
    final[code] = {'code': code, 'http': http, 'title': title, 'attempts': attempts}
    # pending: transport failure on the LAST attempt while never live
    last = r2.get(code) or r1.get(code) or v
    if not title and last.get('http') == 0:
        pending.append({'code': code, 'invite': 'https://chat.whatsapp.com/' + code,
                        'reason': 'transport failed (curl error/timeout) on last attempt; attempts=%d' % attempts})
    elif not title and http == 0:
        pending.append({'code': code, 'invite': 'https://chat.whatsapp.com/' + code,
                        'reason': 'transport failed (curl error/timeout); attempts=%d' % attempts})

json.dump(list(final.values()), open('team08_verify_final.json', 'w'), ensure_ascii=False, indent=0)
# build script reads team08_verify_slice.json; point it at final
json.dump(list(final.values()), open('team08_verify_slice.json', 'w'), ensure_ascii=False, indent=0)
json.dump(pending, open('team08-pending.json', 'w'), ensure_ascii=False, indent=1)

live = sum(1 for v in final.values() if v['http'] == 200 and v['title'])
amb = sum(1 for v in final.values() if v['http'] == 200 and not v['title'])
non200 = sum(1 for v in final.values() if v['http'] not in (200, 0))
err = sum(1 for v in final.values() if v['http'] == 0)
print(f'final: total={len(final)} live={live} dead_ambig={amb} non200={non200} transport0={err} pending={len(pending)}')
print('recovered in retries:', sum(1 for v in final.values() if v['title'] and not pass1[v['code']].get('title')))
