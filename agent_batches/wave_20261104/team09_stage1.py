#!/usr/bin/env python3
"""Team09 stage 1: harvest detail ids per linkado.app category."""
import requests, re, json, time, os

UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
CATS = ['carros','cidades','comprar-e-venda','figurinhas','fitness','lgbt',
        'moda-e-beleza','musica','namoro','series','status','games','tecnologia']
OUT = 'team09_scratch_ids.json'

def new_session():
    s = requests.Session(); s.headers.update(UA); return s

def get(s, url, tries=8):
    for i in range(tries):
        try:
            r = s.get(url, timeout=30)
            if r.status_code == 200: return r
            print('HTTP', r.status_code, url, flush=True)
        except Exception as e:
            print('ERR', type(e).__name__, url, 'try', i, flush=True)
            s.close(); s = new_session()
        time.sleep(5)
    return None

def main():
    out = {}
    if os.path.exists(OUT): out = json.load(open(OUT))
    s = new_session()
    for c in CATS:
        if c in out and out[c].get('done'):
            print(c, 'cached', len(out[c]['ids'])); continue
        ids, pages = set(), [1]
        base = f'https://linkado.app/categoria/{c}'
        maxpage = None
        failed = False
        n = 1
        while True:
            url = base if n == 1 else f'{base}?page={n}'
            r = get(s, url)
            if r is None:
                print(c, 'FAILED page', n); failed = True; break
            h = r.text
            pgids = set(re.findall(r'/grupo/([a-f0-9]{24})', h))
            if not pgids: print(c, 'page', n, 'empty, stop'); break
            new = pgids - ids
            ids |= pgids
            pm = [int(p) for p in re.findall(r'page=(\d+)', h)]
            if maxpage is None and pm: maxpage = max(pm)
            print(c, 'page', n, 'ids', len(pgids), 'new', len(new), 'maxpage', maxpage, flush=True)
            n += 1
            if maxpage and n > maxpage: break
            if n > 60: print(c, 'page cap hit'); failed = True; break
            time.sleep(3)
        out[c] = {'ids': sorted(ids), 'done': not failed}
        json.dump(out, open(OUT, 'w'))
    total = sum(len(v['ids']) for v in out.values())
    print('TOTAL unique ids:', total)

if __name__ == '__main__':
    main()
