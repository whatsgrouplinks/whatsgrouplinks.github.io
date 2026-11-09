#!/usr/bin/env python3
"""Team24 verify: sequential curl checks of chat.whatsapp.com for fresh codes.
LIVE only if HTTP 200 AND non-empty og:title. Empty og:title -> retry up to 2x spaced apart.
Transport failure (curl error / no output) -> pending."""
import json, re, subprocess, html, time

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))

todo = []  # (code, source, meta)
gz = json.load(open(WAVE+'team24_raw/groupizo12_codes.json'))
for code, v in gz.items():
    if code not in union:
        todo.append((code, 'groupizo', v))
det = json.load(open(WAVE+'team24_raw/igrupos_details.json'))
new = json.load(open(WAVE+'team24_raw/igrupos_new.json'))
for gid, v in det.items():
    if v and v['codes']:
        code = v['codes'][0]
        if code not in union:
            m = dict(new['cards'].get(gid, {}))
            m['gid'] = gid
            m['detail_desc'] = v.get('detail_desc','')
            m['category_raw'] = v.get('category_raw','')
            todo.append((code, 'igrupos', m))
print(f'to verify: {len(todo)} (groupizo {sum(1 for _,s,_ in todo if s=="groupizo")}, igrupos {sum(1 for _,s,_ in todo if s=="igrupos")})', flush=True)
json.dump([{'code':c,'source':s,'meta':m} for c,s,m in todo],
          open(WAVE+'team24_raw/verify_todo.json','w'), ensure_ascii=False, indent=1)

TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)
def check(code):
    """returns (status, http_code, title, attempts)"""
    attempts = 0
    for attempt in range(3):
        attempts += 1
        try:
            r = subprocess.run(['curl','-s','-m','25','-A',UA,'-w','\n%{http_code}',
                                f'https://chat.whatsapp.com/{code}'],
                               capture_output=True, text=True, timeout=35)
            out = r.stdout or ''
            lines = out.rsplit('\n', 1)
            http_code = lines[1].strip() if len(lines) > 1 else ''
            body = lines[0] if len(lines) > 1 else out
            if not body.strip():
                if attempt < 2:
                    time.sleep(6); continue
                return ('transport', http_code, '', attempts)
            m = TITLE_RE.search(body)
            title = html.unescape(m.group(1)).strip() if m else ''
            if not title or title in ('WhatsApp Group', 'Join this group on WhatsApp'):
                if attempt < 2:
                    time.sleep(6); continue
                return ('dead-empty', http_code, title, attempts)
            return ('live', http_code, title, attempts)
        except Exception as e:
            if attempt < 2:
                time.sleep(6); continue
            return ('transport', '', '', attempts)
    return ('dead-empty', '', '', attempts)

results = []
done_codes = set()
try:
    for line in open(WAVE+'team24_verify_raw.jsonl'):
        r = json.loads(line)
        done_codes.add(r['code'])
        results.append(r)
    print(f'resuming: {len(results)} already checked', flush=True)
except FileNotFoundError:
    pass
outf = open(WAVE+'team24_verify_raw.jsonl','a')
for i, (code, src, meta) in enumerate(todo):
    if code in done_codes:
        continue
    st, hc, title, att = check(code)
    rec = {'code': code, 'source': src, 'status': st, 'http': hc,
           'title': title, 'attempts': att, 'meta': meta}
    results.append(rec)
    outf.write(json.dumps(rec, ensure_ascii=False)+'\n'); outf.flush()
    print(f"{i+1}/{len(todo)} {st} {code} [{src}] http={hc} att={att} | {title[:60]}", flush=True)
    time.sleep(0.7)
outf.close()
json.dump(results, open(WAVE+'team24_verify_raw.json','w'), ensure_ascii=False, indent=1)
live = sum(1 for r in results if r['status']=='live')
dead = sum(1 for r in results if r['status']=='dead-empty')
trans = sum(1 for r in results if r['status']=='transport')
print(f'VERIFY DONE live={live} dead-empty={dead} transport={trans}', flush=True)
