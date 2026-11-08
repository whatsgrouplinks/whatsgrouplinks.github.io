"""Team 18 verify: og:title liveness check for extracted (name, code) pairs.
Input: team18_raw.json. Output: team18_verified_raw.json + team18_pending_raw.json"""
import requests, re, time, json, os, html as ihtml
from concurrent.futures import ThreadPoolExecutor

WORK = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CODE_RE = re.compile(r'^[A-Za-z0-9]{20,24}$')

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"})
    adapter = requests.adapters.HTTPAdapter(pool_connections=40, pool_maxsize=40, max_retries=1)
    s.mount("https://", adapter)
    return s

SESS = make_session()

def check(item):
    """item = (name, code, slug). Returns (status, og_title, og_desc)."""
    name, code, slug = item
    url = "https://chat.whatsapp.com/invite/" + code
    try:
        r = SESS.get(url, timeout=55)
    except Exception as e:
        return ("transport", "", "")
    if r.status_code == 429:
        return ("rate-limited", "", "")
    t = r.text
    m = re.search(r'<meta[^>]+property="og:title"[^>]*>', t)
    title = ""
    if m:
        c = re.search(r'content="([^"]*)"', m.group(0))
        if c:
            title = ihtml.unescape(c.group(1)).strip()
    m2 = re.search(r'<meta[^>]+property="og:description"[^>]*>', t)
    desc = ""
    if m2:
        c = re.search(r'content="([^"]*)"', m2.group(0))
        if c:
            desc = ihtml.unescape(c.group(1)).strip()
    if title:
        return ("live", title, desc)
    return ("dead", "", desc)

if __name__ == "__main__":
    union = set(json.load(open(os.path.join(WORK, "dedupe_union.json"))))
    print("union size", len(union))
    raw = json.load(open(os.path.join(WORK, "team18_raw.json")))["pages"]
    items, seen, skipped_union, skipped_bad = [], set(), 0, 0
    for slug, v in raw.items():
        for name, code in v.get("pairs", []):
            if not CODE_RE.match(code):
                skipped_bad += 1
                continue
            if code in union or code in seen:
                skipped_union += 1
                continue
            seen.add(code)
            items.append((name, code, slug))
    print("candidates:", len(items), "skipped_union/dup:", skipped_union, "bad:", skipped_bad)

    live, pending, dead = [], [], 0
    import threading
    lock = threading.Lock()
    n429 = [0]

    def work(it):
        st, title, desc = check(it)
        name, code, slug = it
        with lock:
            if st == "live":
                live.append({"name": name, "code": code, "og_title": title,
                             "og_desc": desc, "slug": slug})
            elif st == "dead":
                pass
            else:
                if st == "rate-limited":
                    n429[0] += 1
                pending.append({"name": name, "code": code, "slug": slug,
                                "note": st})
        return st

    with ThreadPoolExecutor(max_workers=24) as ex:
        list(ex.map(work, items))

    json.dump(live, open(os.path.join(WORK, "team18_verified_raw.json"), "w"), ensure_ascii=False)
    json.dump(pending, open(os.path.join(WORK, "team18_pending_raw.json"), "w"), ensure_ascii=False)
    print("LIVE:", len(live), "PENDING:", len(pending), "rate-limited hits:", n429[0])
