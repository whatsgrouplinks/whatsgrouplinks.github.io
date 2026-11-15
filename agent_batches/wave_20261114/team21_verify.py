import requests, re, json, time, html
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
s = requests.Session(); s.headers.update(UA)
def check(code):
    try:
        r = s.get('https://chat.whatsapp.com/'+code, timeout=75)
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
        title = html.unescape(m.group(1)) if m else ''
        return {'code': code, 'status': r.status_code, 'og_title': title, 'bytes': len(r.text), 'live': bool(title.strip())}
    except Exception as e:
        return {'code': code, 'status': None, 'og_title': 'ERR:'+str(e), 'bytes': 0, 'live': False, 'transport_error': True}
fresh = [('EragQCCKHYiDMzne1RZ0Xw','Crypto Trading Signals'),
         ('IfhZ4VcooSsKATEqHiI9y3','SGZCHAT.COM'),
         ('IUkepBFzeoI4MQEAEHHjnj','Job vacancy'),
         ('L98IdHX9BRwBhN7DTTKZpi','TATKAL TICKET AGENCY')]
res = []
for code, name in fresh:
    r = check(code)
    print(code, '|', name, '| status', r['status'], '| live:', r['live'], '| og:title:', repr(r['og_title'][:100]), '| bytes', r['bytes'])
    res.append(r)
    time.sleep(6)
# spaced retry for any empty/non-live without transport error
for r in res:
    if not r['live'] and not r.get('transport_error'):
        print('retrying', r['code'])
        time.sleep(20)
        r2 = check(r['code'])
        print('  retry:', r2['status'], repr(r2['og_title'][:100]), 'bytes', r2['bytes'])
        r['retry'] = r2
        if r2['live']: r['live'] = True; r['og_title'] = r2['og_title']
json.dump(res, open('team21-verify-fresh.json','w'), indent=1, ensure_ascii=False)
