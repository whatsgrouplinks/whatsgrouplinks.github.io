import re, json, html, os, sys, time
import requests
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(line_buffering=True)
WD = os.path.dirname(os.path.abspath(__file__))
PAGES = [
    ("https://www.grouplinksforyou.com/2023/04/pubg-whatsapp-group-links.html?m=1", "Gaming"),
    ("https://www.grouplinksforyou.com/2023/04/free-fire-whatsapp-group-link.html?m=1", "Gaming"),
    ("https://www.asiamediajournal.com/gaming-whatsapp-group-links/", "Gaming"),
    ("https://www.asiamediajournal.com/free-fire-whatsapp-group-links/", "Gaming"),
    ("https://killarnation.com/free-fire-whatsapp-groups-link/", "Gaming"),
    ("https://trickswire.com/whatsapp-group/", "Gaming"),
    ("https://whatsgroupslinkspk.com/", "Gaming"),
    ("https://hubrecipes.com/active-whatsapp-group-links/", "Gaming"),
    ("https://hubrecipes.com/best-movies-whatsapp-group-links/", "Movies"),
    ("https://joingram.in/free-fire-id-buy-sell-whatsapp-groups/", "Buy-Sell"),
    ("https://whtsgrouplink.com/movies-whatsapp-group-links/", "Movies"),
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?!invite/)([A-Za-z0-9]{20,24})(?![A-Za-z0-9])")
INVITE_RE = re.compile(r"chat\.whatsapp\.com/invite/([A-Za-z0-9]{20,24})(?![A-Za-z0-9])")
TAG_RE = re.compile(r"<[^>]+>")

union = set(json.load(open(os.path.join(WD, "dedupe_union.json"))))
print("union size:", len(union), flush=True)

def clean_name(txt):
    txt = html.unescape(txt).strip()
    txt = re.sub(r"\s+", " ", txt)
    txt = re.sub(r"^(Join Here|Join Now|Click Here|Join|Join Link\s*✓|Join ✓)\s*[-–—:|•]*\s*", "", txt, flags=re.I)
    txt = re.sub(r"\s*[-–—:|•]*\s*(Join Here|Join Now|Click Here|Join Link\s*✓|Join)\s*$", "", txt, flags=re.I)
    return txt.strip("-–—:|• ").strip()

def fetch(item):
    url, cat = item
    for i in range(4):
        try:
            s = requests.Session()
            s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
            r = s.get(url, timeout=60, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 1000:
                print("OK", url, len(r.text), "try", i, flush=True)
                return url, cat, r.text
            print("BAD", r.status_code, url, "try", i, flush=True)
        except Exception as e:
            print("try", i, "fail", url, repr(e)[:90], flush=True)
        time.sleep(6 * (i + 1))
    return url, cat, None

with ThreadPoolExecutor(max_workers=4) as ex:
    fetched = {url: (cat, h) for url, cat, h in ex.map(fetch, PAGES)}

allc = []
seen = set()
invite_skipped = 0
for url, cat in PAGES:
    cat, html_t = fetched[url]
    if not html_t:
        continue
    invite_skipped += len(INVITE_RE.findall(html_t))
    for m in CODE_RE.finditer(html_t):
        code = m.group(1)
        if code in union or code in seen:
            continue
        start = max(0, m.start() - 600)
        ctx = html_t[start:m.start()]
        txt = clean_name(TAG_RE.sub(" ", ctx))[-160:]
        seen.add(code)
        allc.append({"code": code, "raw_name": txt, "src": url, "category": cat})

json.dump(allc, open(os.path.join(WD, "team27_candidates.json"), "w"), ensure_ascii=False, indent=1)
print("candidates:", len(allc), "invite-format skipped:", invite_skipped, flush=True)
