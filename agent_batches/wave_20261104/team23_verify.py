import requests, re, html, json, pickle, time, sys

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)

union = pickle.load(open('team23_union.pkl','rb'))
seen = set()

def new_session():
    s = requests.Session()
    s.headers.update({'User-Agent': UA})
    return s

def og_title(sess, code):
    url = 'https://chat.whatsapp.com/' + code
    try:
        r = sess.get(url, timeout=55)
        m = OG_RE.search(r.text)
        title = html.unescape(m.group(1)).strip() if m else ''
        return title
    except Exception as e:
        return 'TRANSPORT:' + type(e).__name__

if __name__ == '__main__':
    cands = json.load(open(sys.argv[1]))
    sess = new_session()
    verified, pending, dropped = [], [], 0
    for c in cands:
        code = c['code']
        if code in union or code in seen:
            continue
        seen.add(code)
        title = og_title(sess, code)
        if title.startswith('TRANSPORT:'):
            sess = new_session()
            pending.append({**c, 'note': 'transport failure: ' + title})
            print('PENDING', code, title)
            continue
        if not title:
            print('DEAD', code)
            continue
        dropped_reason = c.get('drop_if')
        if dropped_reason:
            dropped += 1
            print('DROPPED', code, dropped_reason)
            continue
        name = title
        verified.append({'name': name, 'category': c['category'], 'country': c['country'],
                         'description': c['description'],
                         'invite': 'https://chat.whatsapp.com/' + code, 'image': ''})
        union.add(code)
        print('VERIFIED', code, '|', name)
        time.sleep(0.4)
    json.dump(verified, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(pending, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('verified=%d pending=%d dropped=%d' % (len(verified), len(pending), dropped))
