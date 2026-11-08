#!/usr/bin/env python3
"""Team04: groupchatconnect.info — sitemap -> detail pages -> /go/ codes + metadata.
Checkpointed in team04_scratch/. Run stages via argv: sitemap | details | build"""
import requests, re, json, time, sys, html, os
from concurrent.futures import ThreadPoolExecutor

BASE = "https://groupchatconnect.info"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
SCR = "team04_scratch"
os.makedirs(SCR, exist_ok=True)

def new_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
    return s

def get_with_retry(s, url, timeout=45, tries=4):
    for a in range(tries):
        try:
            r = s.get(url, timeout=timeout)
            if r.status_code == 200 and len(r.text) > 5000:
                return r.text
        except Exception:
            pass
        time.sleep(2 + a * 4)
    return None

def stage_sitemap():
    s = new_session()
    t = get_with_retry(s, BASE + "/sitemap.xml", tries=5)
    if not t:
        print("SITEMAP FAILED"); return
    open(f"{SCR}/sitemap.xml", "w", encoding="utf-8").write(t)
    ids = sorted(set(re.findall(r'groupchatconnect\.info/groupe/(\d+)', t)), key=int)
    ch_ids = sorted(set(re.findall(r'groupchatconnect\.info/(?:en/)?channel/(\d+)', t)), key=int)
    print("groupe ids:", len(ids), "channel ids (excluded):", len(ch_ids))
    print("id range:", ids[0], "-", ids[-1])
    json.dump({"groupe_ids": ids, "channel_ids": ch_ids}, open(f"{SCR}/ids.json", "w"))

def parse_detail(h, gid):
    d = {"id": gid}
    m = re.search(r'<a href="/go/([A-Za-z0-9]{20,24})"', h)
    d["go_code"] = m.group(1) if m else None
    # Telegram groups have no WhatsApp code — flag and skip later
    d["is_telegram"] = ("تلغرام" in h[:30000]) and (d["go_code"] is None)
    # name: h1 is the clean group title
    mh = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    h1_end = 0
    if mh:
        d["name"] = html.unescape(re.sub(r'<[^>]+>', '', mh.group(1))).strip()
        h1_end = mh.end()
    else:
        mt = re.search(r'<meta property="og:title"\s+content="([^"]+)"', h)
        d["name"] = html.unescape(mt.group(1)).strip() if mt else ""
    # badges: FIRST badge container after h1 = this group's badges
    d["cat_ar"] = d["country_ar"] = d["lang_ar"] = ""
    d["plus18"] = False
    bm = re.search(r'<div class="d-flex flex-wrap gap-2 mt-2">(.*?)</div>\s*</div>', h[h1_end:h1_end+2000], re.S)
    bseg = bm.group(1) if bm else h[h1_end:h1_end+2000]
    badges = re.findall(r'<i class="fas fa-(tag|globe|language|exclamation-circle)[^>]*></i>\s*([^<]+?)\s*</span>', bseg)
    for icon, text in badges:
        text = html.unescape(text).strip()
        if icon == 'tag': d["cat_ar"] = text
        elif icon == 'globe': d["country_ar"] = text
        elif icon == 'language': d["lang_ar"] = text
        elif icon == 'exclamation-circle': d["plus18"] = True
    if re.search(r'\+18', bseg):
        d["plus18"] = True
    # description section
    dm = re.search(r'نبذة عن المجموعة</h2>(.*?)<h2', h, re.S)
    if dm:
        txt = re.sub(r'<[^>]+>', ' ', dm.group(1))
        d["desc_ar"] = re.sub(r'\s+', ' ', html.unescape(txt)).strip()[:800]
    else:
        d["desc_ar"] = ""
    return d

def stage_listings():
    """Fetch /?page=1..71, collect /groupe/<id> per page (catches non-sitemap groups)."""
    def fetch_page(p):
        s = new_session()
        h = get_with_retry(s, f"{BASE}/?page={p}", tries=3)
        if not h:
            return p, []
        return p, sorted(set(re.findall(r'/groupe/(\d+)', h)), key=int)
    allids = {}
    fails = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_page, p): p for p in range(1, 72)}
        for f in futs:
            p, ids = f.result()
            if not ids:
                fails.append(p)
            for i in ids:
                allids[i] = True
            if p % 10 == 0:
                print(f"  page {p}: {len(ids)} ids", flush=True)
    print("listing unique ids:", len(allids), "failed pages:", fails)
    json.dump({"listing_ids": sorted(allids, key=int), "failed_pages": fails},
              open(f"{SCR}/listing_ids.json", "w"))

def fetch_detail(gid):
    s = new_session()
    h = get_with_retry(s, f"{BASE}/groupe/{gid}", tries=3)
    if not h:
        return {"id": gid, "error": "fetch-failed"}
    return parse_detail(h, gid)

def stage_details():
    sm = json.load(open(f"{SCR}/ids.json"))["groupe_ids"]
    extra = []
    if os.path.exists(f"{SCR}/listing_ids.json"):
        extra = json.load(open(f"{SCR}/listing_ids.json"))["listing_ids"]
    ids = sorted(set(sm) | set(extra), key=int)
    print(f"union ids: sitemap {len(sm)} + listing {len(extra)} = {len(ids)}")
    done = {}
    if os.path.exists(f"{SCR}/details.json"):
        done = {d["id"]: d for d in json.load(open(f"{SCR}/details.json"))}
    todo = [i for i in ids if i not in done]
    print(f"ids total {len(ids)}, done {len(done)}, todo {len(todo)}")
    results = []
    def worker(gid):
        try:
            return fetch_detail(gid)
        except Exception as e:
            return {"id": gid, "error": f"exception {type(e).__name__}"}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for n, d in enumerate(ex.map(worker, todo)):
            done[d["id"]] = d
            if (n + 1) % 50 == 0:
                print(f"  {n+1}/{len(todo)}", flush=True)
                json.dump(list(done.values()), open(f"{SCR}/details.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(list(done.values()), open(f"{SCR}/details.json", "w", encoding="utf-8"), ensure_ascii=False)
    ok = sum(1 for d in done.values() if d.get("go_code"))
    print("details:", len(done), "with go_code:", ok)

if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "sitemap"
    if stage == "sitemap":
        stage_sitemap()
    elif stage == "listings":
        stage_listings()
    elif stage == "details":
        stage_details()
