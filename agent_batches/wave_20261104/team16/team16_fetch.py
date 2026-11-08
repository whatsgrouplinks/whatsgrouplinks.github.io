import requests, time, sys
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
CATS = sys.argv[1:] or ['animation','business','cryptocurrency','earning','education','finance','football','friendship','gaming','movies','uncategorized']
s = requests.Session(); s.headers.update(UA)
for c in CATS:
    ok = False
    for att in range(5):
        try:
            r = s.get(f'https://groupwhat.com/category/{c}', timeout=90)
            n = len(r.text)
            if n > 50000:
                with open(f'_cat_{c}.html','w') as f: f.write(r.text)
                print(c, r.status_code, n, 'SAVED', flush=True); ok = True; break
            print(c, 'short', n, 'retry', att, flush=True)
        except Exception as e:
            print(c, 'ERR', type(e).__name__, 'retry', att, flush=True)
        time.sleep(5)
    if not ok: print(c, 'FAILED', flush=True)
    time.sleep(3)
print('DONE', flush=True)
