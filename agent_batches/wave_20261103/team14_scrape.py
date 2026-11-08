#!/usr/bin/env python3
"""Team 14: groupjoin.link NEW tags pagination scrape (parallel curl fetchers)."""
import json, re, time, html, os, subprocess, threading
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
TAGS = ["pakistan","brazil","mexico","nigeria","jobs","music","movies","football",
        "study","crypto","news","health","travel","food","funny","pets"]
WORKERS = 3
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def fetch(tag, page):
    url = f"https://www.groupjoin.link/tag/{tag}/?page={page}&limit=20&safeSearch=blur"
    for attempt in range(3):
        try:
            out = subprocess.run(
                ["curl","-sL","--max-time","120","--retry","1","-A",UA,url],
                capture_output=True, text=True, timeout=140)
            if out.stdout and len(out.stdout) > 1000:
                return out.stdout
        except Exception:
            pass
        time.sleep(3)
    return ""

def parse_records(page_html, tag):
    t = page_html.replace('\\"','"').replace('\\u0026','&')
    total_m = re.search(r'"currentCount":(\d+)', t)
    records = []
    seen = set()
    for tm in re.finditer(r'"group_title":"((?:[^"\\]|\\.)*)"', t):
        raw_title = tm.group(1)
        try:
            title = bytes(raw_title, "utf-8").decode("unicode_escape").strip()
        except Exception:
            title = raw_title.strip()
        win = t[tm.start():tm.start()+2500]
        lm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', win)
        if not lm:
            continue
        code = lm.group(1)
        if code in seen:
            continue
        seen.add(code)
        def getf(pat):
            m = re.search(pat, win)
            return m.group(1) if m else ""
        def getv(pat):
            m = re.search(pat, win)
            if not m:
                return ""
            try:
                return bytes(m.group(1), "utf-8").decode("unicode_escape").strip()
            except Exception:
                return m.group(1).strip()
        img = getf(r'"group_img":"((?:[^"\\]|\\.)*)"')
        desc = getv(r'"group_desc":"((?:[^"\\]|\\.)*)"')
        cat_name = getf(r'"category_name":"([^"]*)"')
        cat_slug = getf(r'"category_slug":"([^"]*)"')
        iso2 = getf(r'"iso2":"([A-Z]{2})"')
        records.append({"code": code, "title": html.unescape(title), "cat_slug": cat_slug,
                        "cat_name": cat_name, "country": iso2, "desc": html.unescape(desc),
                        "img": img, "tag": tag})
    return records, (int(total_m.group(1)) if total_m else None)

lock = threading.Lock()
raw = {}
out_path = os.path.join(WAVE, "team14_raw.json")
if os.path.exists(out_path):
    raw = json.load(open(out_path))

def save():
    with lock:
        json.dump(raw, open(out_path, "w"), ensure_ascii=False, indent=1)

def scrape_tag(tag):
    try:
        _scrape_tag_inner(tag)
    except Exception as e:
        print(f"{tag}: WORKER ERROR {type(e).__name__}: {e}", flush=True)
        save()

def _scrape_tag_inner(tag):
    pages_done = raw.get(tag, {}).get("pages_scraped", 0)
    recs_done = raw.get(tag, {}).get("records", [])
    page, empty_streak, all_recs = 1, 0, list(recs_done)
    pages = pages_done
    print(f"SCRAPING {tag} ... (resume p{page})", flush=True)
    while True:
        page_html = fetch(tag, page)
        if not page_html:
            print(f"  {tag} p{page}: FETCH FAILED", flush=True)
            empty_streak += 1
            if empty_streak >= 3:
                break
            page += 1
            time.sleep(1)
            continue
        recs, total = parse_records(page_html, tag)
        print(f"  {tag} p{page}: {len(recs)} recs (total~{total})", flush=True)
        pages = page
        if len(recs) == 0:
            empty_streak += 1
            if empty_streak >= 2:
                break
        else:
            empty_streak = 0
        all_recs.extend(recs)
        page += 1
        time.sleep(0.2)
        if page > 600:
            print(f"  {tag}: SAFETY CAP", flush=True)
            break
    with lock:
        raw[tag] = {"records": all_recs, "pages_scraped": pages, "done": True}
    save()

def main():
    from concurrent.futures import as_completed
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        pending = [t for t in TAGS if not (t in raw and raw[t].get("done"))]
        print(f"tags to scrape: {pending}", flush=True)
        futs = {ex.submit(scrape_tag, t): t for t in pending}
        for f in as_completed(futs):
            try:
                f.result()
            except Exception as e:
                print(f"{futs[f]}: FUTURE ERROR {type(e).__name__}: {e}", flush=True)
    print("DONE scraping", flush=True)

if __name__ == "__main__":
    main()
