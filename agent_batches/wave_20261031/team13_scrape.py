#!/usr/bin/env python3
"""team13: scrape whatspgroupslink.com listing posts, dedupe, og:title-verify."""
import json, re, time, html as htmlmod, urllib.request, urllib.error, sys, os

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261031")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{22})(?![A-Za-z0-9])')

BLOCK_WORDS = ["porn", "pornhub", "xxx", "nude", "sex video", "escort", "call girl",
               "fuck", "dick", "pussy", "boobs", "anal", "sexy", "mms",
               "hot night", "desi hot", "18+", "18 +"]
BLOCK_EMOJI = ["🥵", "🍆", "🍑", "🔞", "💦", "👅", "👄", "💋"]

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = htmlmod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def is_blocked(name, row_text=""):
    nl = name.lower()
    for w in BLOCK_WORDS:
        if w in nl:
            return True
    for e in BLOCK_EMOJI:
        if e in row_text:
            return True
    return False

def extract_rows(page_html):
    """Return list of (name, code) from table rows."""
    out = []
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', page_html, re.S | re.I):
        codes = CODE_RE.findall(row)
        if not codes:
            continue
        cells = [clean(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)]
        name = ""
        for cell in cells:
            cl = cell.lower()
            if not cell or cell.isdigit() or cl in ("join", "join now", "join group") \
               or "chat.whatsapp" in cl or len(cell) < 2:
                continue
            name = cell
            break
        for code in codes:
            out.append((name, code, row))
    return out

def fallback_extract(page_html):
    """code occurrences outside tables: name = preceding text."""
    out = []
    for m in CODE_RE.finditer(page_html):
        code = m.group(1)
        before = clean(page_html[max(0, m.start() - 700):m.start()])
        name = before[-160:].strip()
        name = re.sub(r'^(join( now| group)?|#\d+|\d+)[\s\-|:]*', '', name, flags=re.I).strip()
        name = name.split('\n')[-1].strip()
        if len(name) > 120:
            name = name[-120:]
        out.append((name, code, ""))
    return out

def og_title(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        page = fetch(url)
    except Exception as e:
        return None, "transport: %s" % type(e).__name__
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', page, re.I | re.S)
    if not m:
        m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', page, re.I | re.S)
    if not m:
        return "", None
    return clean(m.group(1)), None

CAT_MAP = [
    ("education", "Education"), ("study", "Study Groups"), ("job", "Jobs"),
    ("entertainment", "Entertainment"), ("news", "News"), ("religion", "Islamic"),
    ("crypto", "Crypto"), ("game", "Gaming"), ("marriage", "Family"),
    ("earn-money", "Online Earning"), ("international", "Community & Social"),
    ("girls", "Friendship"), ("actress", "Entertainment"),
]

def category_for(slug, name):
    nl = (slug + " " + name).lower()
    if any(k in nl for k in ["islam", "quran", "muslim", "naat", "madrasa"]):
        return "Islamic"
    for key, cat in CAT_MAP:
        if key in slug.lower():
            return cat
    for key, cat in [("study", "Study Groups"), ("education", "Education"), ("job", "Jobs"),
                     ("sport", "Sports"), ("cricket", "Sports"), ("movie", "Movies"),
                     ("music", "Music"), ("health", "Health"), ("business", "Business"),
                     ("shop", "Shopping"), ("travel", "Travel & Tourism"),
                     ("food", "Food & Drinks"), ("poetry", "Poetry"),
                     ("scholarship", "Scholarships"), ("dating", "Dating & Social"),
                     ("friend", "Friendship"), ("girl", "Friendship"),
                     ("earn", "Online Earning"), ("money", "Online Earning"),
                     ("tech", "Technology"), ("crypto", "Crypto"),
                     ("game", "Gaming"), ("news", "News"),
                     ("comedy", "Comedy & Funny"), ("joke", "Quotes & Jokes"),
                     ("islam", "Islamic"), ("quran", "Islamic"),
                     ("bible", "Religion"), ("hindu", "Religion"),
                     ("christian", "Religion")]:
        if key in nl:
            return cat
    return "General Chat"

def country_for(name, slug):
    nl = (name + " " + slug).lower()
    if "pakistan" in nl or " pak " in nl or "karachi" in nl or "lahore" in nl:
        return "PK"
    return "IN"

def main():
    union = set(l.strip() for l in open("/tmp/union.txt") if l.strip())
    print("union:", len(union), flush=True)

    urls = []
    for f in ("/tmp/p1.xml", "/tmp/p2.xml"):
        urls += re.findall(r'<loc>(https://whatspgroupslink\.com/[^<]+)', open(f).read())
    urls = sorted(set(urls))
    print("posts:", len(urls), flush=True)

    # resume support
    done = set()
    resume_file = "/tmp/team13_done.txt"
    if os.path.exists(resume_file):
        done = set(l.strip() for l in open(resume_file) if l.strip())

    cand = {}  # code -> dict(name, slug)
    todo = [u for u in urls if u not in done]
    print("posts remaining:", len(todo), flush=True)
    import threading
    from concurrent.futures import ThreadPoolExecutor
    lock = threading.Lock()
    done_fh = open(resume_file, "a")

    def scrape_one(url):
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        try:
            page = fetch(url)
        except Exception as e:
            print("fetch fail", url, type(e).__name__, flush=True)
            with lock:
                done_fh.write(url + "\n"); done_fh.flush()
            return
        rows = extract_rows(page)
        if not rows:
            rows = fallback_extract(page)
        local = []
        for name, code, row in rows:
            if code in union:
                continue
            name = name.strip()
            if len(name) < 2 or len(name) > 150:
                continue
            if is_blocked(name, row):
                continue
            local.append((code, name, slug))
        with lock:
            for code, name, slug in local:
                if code not in cand:
                    cand[code] = {"name": name, "slug": slug}
            done_fh.write(url + "\n"); done_fh.flush()

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(scrape_one, u) for u in todo]
        done_count = [0]
        for f in futures:
            f.result()
            done_count[0] += 1
            if done_count[0] % 25 == 0:
                print(f"scraped {done_count[0]}/{len(todo)} posts, candidates: {len(cand)}", flush=True)
    done_fh.close()
    print("total candidates after filters:", len(cand), flush=True)
    json.dump(cand, open("/tmp/team13_cand.json", "w"), ensure_ascii=False, indent=1)

    verified, pending = [], []
    n = 0
    for code, info in cand.items():
        n += 1
        title, err = og_title(code)
        if err and err.startswith("transport"):
            pending.append({"name": info["name"], "category": category_for(info["slug"], info["name"]),
                            "description": "", "image": "",
                            "invite": "https://chat.whatsapp.com/" + code,
                            "country": country_for(info["name"], info["slug"]),
                            "note": "transport failure during og:title check"})
        elif err == "rate-limited":
            pending.append({"name": info["name"], "category": category_for(info["slug"], info["name"]),
                            "description": "", "image": "",
                            "invite": "https://chat.whatsapp.com/" + code,
                            "country": country_for(info["name"], info["slug"]),
                            "note": "rate-limited; resume from code index %d/%d" % (n, len(cand))})
            break
        elif title:
            if is_blocked(title):
                continue
            name = info["name"] if info["name"] else title
            cat = category_for(info["slug"], title)
            country = country_for(title, info["slug"])
            cname = {"IN": "India", "PK": "Pakistan"}.get(country, "worldwide")
            verified.append({
                "name": name,
                "category": cat,
                "description": "%s is an active WhatsApp group for %s lovers in %s. Join %s to chat, share updates and connect with the %s community." % (name, cat.lower(), cname, name, cat.lower()),
                "image": "",
                "invite": "https://chat.whatsapp.com/" + code,
                "country": country,
            })
        time.sleep(0.6)
        if n % 50 == 0:
            print(f"verified {n}/{len(cand)}: {len(verified)} ok, {len(pending)} pending", flush=True)
            json.dump(verified, open(BASE + "/team13-whatspgroupslink-variant.json", "w"), ensure_ascii=False, indent=1)
    json.dump(verified, open(BASE + "/team13-whatspgroupslink-variant.json", "w"), ensure_ascii=False, indent=1)
    if pending:
        json.dump(pending, open(BASE + "/team13-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
    print("DONE verified=%d pending=%d" % (len(verified), len(pending)), flush=True)

if __name__ == "__main__":
    main()
