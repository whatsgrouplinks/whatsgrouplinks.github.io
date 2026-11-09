import json, re, subprocess, html, time, os
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
CKPT = WAVE + 'team10_verify.jsonl'

fresh = json.load(open(WAVE + 'team10_fresh_codes.json'))
done = {}
if os.path.exists(CKPT):
    for line in open(CKPT):
        try:
            r = json.loads(line)
            done[r['code']] = r
        except Exception:
            pass
print('fresh:', len(fresh), '| already done:', len(done), flush=True)

GENERIC = {'whatsapp group', 'join this group on whatsapp', 'whatsapp',
           'join group on whatsapp', 'whatsapp group invite link'}

def og_title(body):
    m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
    if not m:
        m = re.search(r"og:title['\"]?\s*content=['\"]([^'\"]*)", body)
    return html.unescape(m.group(1)).strip() if m else ''

def check(args):
    code, rec = args
    last = 'empty-og-title'
    for attempt in range(2):
        try:
            p = subprocess.run(['curl', '-s', '-m', '30', '-A', UA,
                                'https://chat.whatsapp.com/' + code],
                               capture_output=True, text=True, timeout=40)
            t = og_title(p.stdout or '')
            if t and t.lower() not in GENERIC:
                return {'code': code, 'status': 'live', 'og_title': t,
                        'attempts': attempt + 1, 'url': rec['url'],
                        'page_title': rec['title'], 'page_desc': rec['desc']}
            if t and t.lower() in GENERIC:
                return {'code': code, 'status': 'dead', 'og_title': t,
                        'attempts': attempt + 1, 'url': rec['url'],
                        'page_title': rec['title'], 'page_desc': rec['desc']}
            time.sleep(5)
        except Exception as e:
            last = 'transport:' + str(e)[:60]
            time.sleep(5)
    st = 'pending' if 'transport' in last else 'dead'
    return {'code': code, 'status': st, 'og_title': '', 'attempts': 2,
            'url': rec['url'], 'page_title': rec['title'], 'page_desc': rec['desc']}

items = [(c, r) for c, r in fresh.items() if c not in done]
print('to check:', len(items), flush=True)
fout = open(CKPT, 'a')
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(check, items):
        done[res['code']] = res
        fout.write(json.dumps(res, ensure_ascii=False) + '\n')
        fout.flush()
        print(res['code'], res['status'], '|', res['og_title'][:70], flush=True)
        time.sleep(0.6)
fout.close()

final = {c: {k: v for k, v in r.items() if k != 'code'} for c, r in done.items()}
json.dump(final, open(WAVE + 'team10_verify.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(r['status'] for r in final.values()))
print('DONE', len(final))
