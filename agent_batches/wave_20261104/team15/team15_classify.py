"""TEAM15: classify groupsinvite.link rules pages -> chat vs channel (resume 1800/2326)."""
import json, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

T = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team15'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
BASE = 'https://groupsinvite.link'

_local = threading.local()
def sess():
    s = getattr(_local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _local.s = s
    return s

def fetch_rules(slug):
    url = f'{BASE}/group/rules/{slug}/'
    try:
        r = sess().get(url, timeout=45)
        if r.status_code != 200:
            return slug, 'error', f'http{r.status_code}'
        html = r.text
        # NOTE: /invite/ chat-format codes are CHANNEL-format -> excluded per brief.
        # Take exact case only, never lowercase.
        chats = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})(?![A-Za-z0-9])', html)
        invs = re.findall(r'chat\.whatsapp\.com/invite/([A-Za-z0-9]{20,24})', html)
        chans = re.findall(r'whatsapp\.com/channel/([A-Za-z0-9]{20,24})', html)
        if chats:
            return slug, 'chat', chats[0]
        if chans or invs:
            return slug, 'channel', (chans or invs)[0]
        return slug, 'none', ''
    except Exception as e:
        return slug, 'error', type(e).__name__

def main():
    split = json.load(open(f'{T}/slugs_split.json'))
    slugs = split['grp']  # 0029v*/029v* channel slugs skipped upstream
    print(f'group-candidate slugs: {len(slugs)} (channels skipped: {len(split["chan"])})', flush=True)
    done = {}
    try:
        done = json.load(open(f'{T}/classify.json'))
    except Exception:
        pass
    todo = [s for s in slugs if s not in done]
    print(f'resuming with {len(done)} classified, todo={len(todo)}', flush=True)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_rules, s): s for s in todo}
        n = 0
        for f in as_completed(futs):
            slug, kind, code = f.result()
            done[slug] = {'kind': kind, 'code': code}
            n += 1
            if n % 100 == 0:
                json.dump(done, open(f'{T}/classify.json', 'w'))
                print(f'{n}/{len(todo)}', flush=True)
    json.dump(done, open(f'{T}/classify.json', 'w'))
    from collections import Counter
    print('FINAL classify:', len(done), dict(Counter(x['kind'] for x in done.values())), flush=True)

if __name__ == '__main__':
    main()
