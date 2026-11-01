import re, sys, json, time, urllib.request

D = {}
def load_dedupe(path):
    s = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                s.add(line)
    return s

DEDUP = load_dedupe('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261030/dedupe_union_codes.txt')
print("dedupe codes loaded:", len(DEDUP))

CODE_RE = re.compile(r'https?://chat\.whatsapp\.com/([A-Za-z0-9_-]{22})')
def extract_codes(text):
    return CODE_RE.findall(text)

def is_fresh(code):
    return len(code) == 22 and code not in DEDUP

def verify(code, timeout=25):
    url = 'https://chat.whatsapp.com/' + code
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            html = r.read(50000).decode('utf-8', errors='ignore')
            m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
            title = m.group(1) if m else ''
            if not title or "Couldn't look up link" in title or 'could not be found' in html.lower()[:2000]:
                return False, title
            return True, title
    except Exception as e:
        return False, 'ERR:'+str(e)[:60]

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        codes = json.load(open(sys.argv[2]))
        out = {}
        for c in codes:
            ok, t = verify(c)
            out[c] = [ok, t]
            print(c, ok, '|', t)
            time.sleep(0.5)
        json.dump(out, open(sys.argv[3] if len(sys.argv)>3 else '/tmp/ver.json','w'), indent=1)
