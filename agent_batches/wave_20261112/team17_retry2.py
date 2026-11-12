"""Team17 retry pass 2: pages 4-9 + remaining detail fails, after the
rate-limit cleared (curl probe of p4 returned 200, 244KB, 19 cards).
Slow pacing to avoid re-triggering the bot-check. Merges into outputs."""
import re, json, time, os
import requests
import importlib.util

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
EXISTING = '/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

spec = importlib.util.spec_from_file_location('t17', os.path.join(WAVE, 'team17_mine.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
fetch, parse_listing, og_title = m.fetch, m.parse_listing, m.og_title
CAT, COUNTRY, DROP_RE, NEG_RE, clean = m.CAT, m.COUNTRY, m.DROP_RE, m.NEG_RE, m.clean

existing = set(json.load(open(EXISTING)))
cands = json.load(open(os.path.join(WAVE, 'team17-tugrupo-online-candidates.json')))
pend = json.load(open(os.path.join(WAVE, 'team17-tugrupo-online-pending.json')))
leads = json.load(open(os.path.join(WAVE, 'team17-tugrupo-online-leads.json')))
summary = json.load(open(os.path.join(WAVE, 'team17-tugrupo-online-summary.json')))
banked_codes = {c['invite'].split('/')[-1] for c in cands} | {p.get('invite', '').split('/')[-1] for p in pend}

done_details, seen_codes = set(), set()
for line in open(os.path.join(WAVE, 'team17_progress.jsonl'), encoding='utf-8'):
    d = json.loads(line)
    done_details.add(d['detail']); seen_codes.add(d['code'])
print(f'start retry2: banked={len(cands)} done_details={len(done_details)}', flush=True)

sess = requests.Session(); sess.headers.update(UA)
ckpt = open(os.path.join(WAVE, 'team17_progress.jsonl'), 'a', encoding='utf-8')
new_mined, pages_done, pages_failed, detail_fail = [], [], [], []

retry_details = [u for u in leads if '/whatsapp/' in u and 'query-eb715b85' not in u]
for url in retry_details:
    if url in done_details:
        continue
    dh = fetch(sess, url)
    if not dh:
        detail_fail.append(url); continue
    mm = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,40})', dh)
    if not mm:
        detail_fail.append(url); continue
    t = og_title(dh).replace(' Grupo de WhatsApp', '').strip(' "')
    rec = {'detail': url, 'cat_es': '', 'country_es': '', 'title': t, 'excerpt': '',
           'code': mm.group(1), 'detail_title': og_title(dh)}
    new_mined.append(rec); done_details.add(url)
    ckpt.write(json.dumps(rec, ensure_ascii=False) + '\n'); ckpt.flush()
    print('  retry2-detail OK', url, mm.group(1), flush=True)
    time.sleep(6)

for p in range(4, 10):
    url = f'https://tugrupo.online/whatsapp/?query-eb715b85={p}'
    h = fetch(sess, url, tries=4)
    if not h:
        pages_failed.append(p); print(f'RETRY2 PAGE {p} FAILED', flush=True); continue
    cards = parse_listing(h)
    print(f'RETRY2 PAGE {p}: {len(cards)} cards', flush=True)
    pages_done.append(p)
    for c in cards:
        if c['detail'] in done_details:
            continue
        dh = fetch(sess, c['detail'])
        if not dh:
            detail_fail.append(c['detail']); continue
        mm = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,40})', dh)
        if not mm:
            detail_fail.append(c['detail']); continue
        c['code'] = mm.group(1); c['detail_title'] = og_title(dh)
        new_mined.append(c); done_details.add(c['detail'])
        ckpt.write(json.dumps(c, ensure_ascii=False) + '\n'); ckpt.flush()
        time.sleep(5)
    time.sleep(25)
ckpt.close()
print(f'RETRY2 MINED {len(new_mined)} pages_done={pages_done} pages_failed={pages_failed} detail_fail={len(detail_fail)}', flush=True)

excluded, dead, new_pending = [], [], []
kept_before = len(cands)
for c in new_mined:
    code = c['code']
    if code in existing or code in banked_codes:
        continue
    banked_codes.add(code)
    name = c['title'] or c.get('detail_title') or ''
    desc_src = (name + ' ' + c.get('excerpt', '')).lower()
    if DROP_RE.search(desc_src) and not NEG_RE.search(desc_src):
        excluded.append({**c, 'reason': 'content-screen drop: ' + DROP_RE.search(desc_src).group(0)})
        continue
    live_title = None; tf = False
    for attempt in range(3):
        try:
            r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=75)
            if r.status_code == 200:
                live_title = og_title(r.text); break
            tf = True
        except Exception as e:
            tf = True; print(f'  verify {code} ERR {e}', flush=True)
        time.sleep(5)
    if live_title is None and tf:
        new_pending.append({**c, 'reason': 'transport failure on verify'}); continue
    if not live_title:
        dead.append({**c, 'reason': 'no og:title (dead/expired)'}); continue
    if not name:
        name = live_title
    cat = CAT.get(c['cat_es'], 'Community & Social')
    country = COUNTRY.get(c['country_es'], '')
    desc = f"Join {name}, a WhatsApp group listed under {cat}" + (f" from {c['country_es']}." if c['country_es'] and c['country_es'] != 'Mundial' else ".")
    if c.get('excerpt'):
        desc += ' ' + clean(c['excerpt'])[:200]
    cands.append({'name': name, 'category': cat, 'country': country,
                  'description': desc, 'invite': f'https://chat.whatsapp.com/{code}'})
    print(f'  LIVE {code} {name!r}', flush=True)

pend.extend(new_pending)
new_leads = [f'https://tugrupo.online/whatsapp/?query-eb715b85={p}' for p in pages_failed] + detail_fail
json.dump(cands, open(os.path.join(WAVE, 'team17-tugrupo-online-candidates.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(pend, open(os.path.join(WAVE, 'team17-tugrupo-online-pending.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(new_leads, open(os.path.join(WAVE, 'team17-tugrupo-online-leads.json'), 'w'), ensure_ascii=False, indent=1)
summary['retry_pass2'] = {
    'pages_done': pages_done, 'pages_failed': pages_failed,
    'new_mined': len(new_mined), 'new_verified_kept': len(cands) - kept_before,
    'new_pending': len(new_pending), 'new_dead': len(dead),
    'new_exclusions': excluded, 'detail_fail': len(detail_fail)}
summary['verified_kept'] = len(cands)
summary['pending'] = len(pend)
summary['leads'] = len(new_leads)
summary['mined_listings'] = summary['mined_listings'] + len(new_mined)
summary['dead_no_og_title'] = summary['dead_no_og_title'] + len(dead)
summary['exclusions'] = summary.get('exclusions', []) + excluded
summary['pages_done'] = sorted(set(summary['pages_done']) | set(pages_done))
summary['pages_failed'] = pages_failed
summary['resume'] = (f"Retry2: pages {pages_done} recovered, still failed: {pages_failed}; "
                      f"detail-fail URLs remaining: {len(detail_fail)} (in leads file). "
                      f"Slice pages mined overall: {summary['pages_done']}.")
json.dump(summary, open(os.path.join(WAVE, 'team17-tugrupo-online-summary.json'), 'w'), ensure_ascii=False, indent=1)
print('RETRY2 SUMMARY', json.dumps(summary['retry_pass2'], ensure_ascii=False), flush=True)
print('TOTALS candidates=', len(cands), 'pending=', len(pend), 'leads=', len(new_leads), flush=True)
