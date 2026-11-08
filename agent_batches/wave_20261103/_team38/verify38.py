import json, re, time, html, sys
import requests
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/"
union = set(json.load(open(WAVE + "dedupe_union.json")))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
def check(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
        m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', r.text, re.S|re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]*property=["\']og:title["\']', r.text, re.S|re.I)
        title = html.unescape(m.group(1)).strip() if m else ""
        return ("ok", title)
    except Exception as e:
        return ("transport", type(e).__name__)
def verify(codes):
    verified, pending, skipped, dead = [], [], 0, 0
    own = set()
    for i, code in enumerate(codes):
        if code in union or code in own:
            skipped += 1; continue
        own.add(code)
        st, title = check(code)
        time.sleep(0.7)
        if st == "transport":
            pending.append(code)
        elif title:
            verified.append((code, title))
        else:
            dead += 1
        if (i+1) % 20 == 0:
            print(f"  progress {i+1}/{len(codes)} v={len(verified)} p={len(pending)} d={dead} s={skipped}", file=sys.stderr, flush=True)
    return verified, pending, skipped, dead
