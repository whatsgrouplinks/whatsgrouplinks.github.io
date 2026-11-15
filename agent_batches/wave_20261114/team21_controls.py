import requests, re, json, time
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
s = requests.Session(); s.headers.update(UA)
def og_title(code):
    try:
        r = s.get('https://chat.whatsapp.com/'+code, timeout=75)
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
        if not m:
            m = re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", r.text)
        return r.status_code, (m.group(1) if m else ''), len(r.text)
    except Exception as e:
        return None, 'ERR:'+str(e), 0
for code, expect in [('KrDwdK8EIkB6vgauHg5M7N','JAY - PHP & Python Full Stack Developer'),
                     ('ZzZzZzZzZzZzZzZzZzZzZzZz','')]:
    st, title, n = og_title(code)
    print(code, '| status', st, '| bytes', n, '| og:title=', repr(title), '| expect:', repr(expect), '| PASS' if title==expect else '| FAIL')
    time.sleep(3)
