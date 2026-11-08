#!/usr/bin/env python3
"""Team39: extract candidates (name+code) from saved probe HTML, dedupe vs union,
verify via og:title with keep-alive session, write verified items."""
import re, os, sys, json, pickle, html, requests, concurrent.futures

WD = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team39_work')
union = pickle.load(open(WD + '/union.pkl', 'rb'))
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}

PORN_RE = re.compile(r'(?i)\b(porn|pornhub|xxx|nude|sex\s*video|escort|call\s*girl|fuck|dick|pussy|boobs|anal|bokep|satta|matka)\b|مزا\s*دینے|مزہ\s*دینے')
EMOJI_RE = re.compile('[\U0001F975\U0001F346\U0001F351\U0001F51E\U0001F4A6\U0001F445\U0001F444\U0001F48B]')

def extract(label):
    t = open(f'{WD}/probe_{label}.html').read()
    # find table rows with name + link: capture text around chat.whatsapp.com/<code>
    cands = []
    for m in re.finditer(r'chat\.whatsapp\.com/(?!invite/)([A-Za-z0-9]{20,24})(?![A-Za-z0-9])', t):
        code = m.group(1)
        start = max(0, m.start() - 600)
        window = re.sub(r'<[^>]+>', ' ', t[start:m.start()])
        window = html.unescape(re.sub(r'\s+', ' ', window)).strip()
        name = window[-140:] if len(window) > 140 else window
        cands.append((code, name))
    return cands

def verify_one(args):
    code, name, cat, country = args
    s = requests.Session()
    s.headers.update(UA)
    try:
        r = s.get(f'https://chat.whatsapp.com/{code}', timeout=60)
        t = r.text
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', t)
        if not m:
            return ('dead', code, name, '')
        title = html.unescape(m.group(1)).strip()
        if not title:
            return ('dead', code, name, '')
        return ('live', code, title, '')
    except Exception as e:
        return ('pending', code, name, str(e)[:80])

if __name__ == '__main__':
    print('stub - run via extract/verify step scripts', file=sys.stderr)
