"""TEAM 30R: harvest groupsinvite.link rules pages -> classify chat vs channel."""
import json, re, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
BASE = 'https://groupsinvite.link'

def fetch_rules(slug):
    """Return (slug, kind, code) where kind in chat|channel|none|error."""
    url = f'{BASE}/group/rules/{slug}/'
    try:
        r = requests.get(url, headers=UA, timeout=25)
        if r.status_code != 200:
            return slug, 'error', f'http{r.status_code}'
        html = r.text
        chats = re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', html)
        chans = re.findall(r'whatsapp\.com/channel/([A-Za-z0-9]{20,24})', html)
        if chats:
            return slug, 'chat', chats[0]
        if chans:
            return slug, 'channel', chans[0]
        return slug, 'none', ''
    except Exception as e:
        return slug, 'error', type(e).__name__

def main():
    split = json.load(open('/tmp/team30r/slugs_split.json'))
    slugs = split['grp']  # channel-pattern slugs (0029v/029v) skipped: channels NEVER allowed
    print(f'group-candidate slugs to classify: {len(slugs)} (channels skipped: {len(split["chan"])})', flush=True)
    done = {}
    try:
        done = json.load(open('/tmp/team30r/classify.json'))
        print(f'resuming with {len(done)} already classified', flush=True)
    except Exception:
        pass
    todo = [s for s in slugs if s not in done]
    print(f'todo: {len(todo)}', flush=True)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_rules, s): s for s in todo}
        n = 0
        for f in as_completed(futs):
            slug, kind, code = f.result()
            done[slug] = {'kind': kind, 'code': code}
            n += 1
            if n % 100 == 0:
                json.dump(done, open('/tmp/team30r/classify.json', 'w'))
                kinds = {}
                for v in done.values():
                    kinds[v['kind']] = kinds.get(v['kind'], 0) + 1
                print(f'{n}/{len(todo)} classified; totals {kinds}', flush=True)
    json.dump(done, open('/tmp/team30r/classify.json', 'w'))
    kinds = {}
    for v in done.values():
        kinds[v['kind']] = kinds.get(v['kind'], 0) + 1
    print('FINAL:', kinds, flush=True)

if __name__ == '__main__':
    main()
