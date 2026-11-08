import json, re, requests, collections
from concurrent.futures import ThreadPoolExecutor, as_completed
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/'
def ids(p):
    try:
        r = requests.get('https://linkado.app/categoria/amizade?page=%d'%p, headers={'User-Agent':UA}, timeout=90)
        return (p, sorted(set(re.findall(r'/grupo/([a-f0-9]{24})', r.text))))
    except Exception:
        return (p, [])
res = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(ids, p): p for p in range(1, 151)}
    done = 0
    for f in as_completed(futs):
        p, l = f.result()
        res[str(p)] = l
        done += 1
        if done % 30 == 0: print('  %d/150' % done, flush=True)
json.dump(res, open(WAVE+'team10-page-sets.json','w'))
sig = collections.defaultdict(list)
for p, l in res.items():
    sig[tuple(l)].append(int(p))
print('distinct page-contents:', len(sig), flush=True)
for s, pages in sorted(sig.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print('  %d pages share %d ids: pages %s' % (len(pages), len(s), sorted(pages)[:15]), flush=True)
