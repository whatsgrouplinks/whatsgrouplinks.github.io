#!/usr/bin/env python3
"""team07 harvest: groupjoin.link /category/entertainment (id=10) and /category/online-shopping (id=38).
Fetches listing pages via api.groupjoin.link, extracts 22-char invite codes,
dedupes against the 3-source union, saves candidate records to /tmp/team07_candidates.json."""
import json, re, time, subprocess, sys, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
BASE = "https://api.groupjoin.link/groups"
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261101")
SITE = os.path.expanduser("~/workspace/whatsapp-groups-site")

def fetch(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA,
                        "-H", "Origin: https://www.groupjoin.link",
                        "-H", "Referer: https://www.groupjoin.link/",
                        "-w", "\n%{http_code}", url],
                       capture_output=True, text=True, timeout=60)
    out = r.stdout
    if not out.strip():
        return None, 0
    code = out.rsplit("\n", 1)[-1].strip()
    body = out.rsplit("\n", 1)[0]
    try:
        http = int(code)
    except ValueError:
        http = 0
    return body, http

def code_of(link):
    if "/invite/" in link:
        return None
    m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9]+)", link)
    if not m:
        return None
    c = m.group(1)
    return c if re.fullmatch(r"[A-Za-z0-9]{22}", c) else None

def load_exclusion():
    excl = set()
    # (a) groups.json
    gj = os.path.join(SITE, "groups.json")
    if os.path.exists(gj):
        d = json.load(open(gj))
        items = d if isinstance(d, list) else d.get("groups", d.get("items", []))
        for it in items:
            inv = it.get("invite", "") if isinstance(it, dict) else ""
            m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9]{22})", inv or "")
            if m:
                excl.add(m.group(1))
    # (b) .existing_codes.json
    ec = os.path.join(SITE, ".existing_codes.json")
    if os.path.exists(ec):
        d = json.load(open(ec))
        codes = d if isinstance(d, list) else d.get("codes", [])
        for c in codes:
            if isinstance(c, str) and re.fullmatch(r"[A-Za-z0-9]{22}", c):
                excl.add(c)
    # (c) wave_20261031 verified outputs
    prev = os.path.join(SITE, "agent_batches/wave_20261031")
    for fn in os.listdir(prev):
        if not fn.startswith("team") or fn.endswith("-leads.json") or fn.endswith("-unverified-pending.json"):
            continue
        if not fn.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(prev, fn)))
        except Exception:
            continue
        if not isinstance(d, list):
            continue
        for it in d:
            if not isinstance(it, dict):
                continue
            inv = it.get("invite", "")
            m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9]{22})", inv or "")
            if m:
                excl.add(m.group(1))
    return excl

def main():
    excl = load_exclusion()
    print(f"exclusion union size: {len(excl)}", flush=True)
    cats = [("entertainment", 10, "Entertainment"), ("online-shopping", 38, "Shopping")]
    candidates = []
    seen = set()
    resume = {"stopped": False, "pages_done": {}}
    for slug, cid, canon in cats:
        pages_done = 0
        total_pages = None
        p = 1
        while True:
            url = f"{BASE}?category={cid}&page={p}&limit=20&safeSearch=blur"
            body, http = fetch(url)
            time.sleep(1.0)
            if http == 429 or body is None:
                resume["stopped"] = True
                resume["pages_done"][slug] = pages_done
                print(f"RATE-LIMITED/transport on {slug} page {p}; stopping", flush=True)
                break
            if http != 200:
                print(f"{slug} page {p}: HTTP {http}; skipping", flush=True)
                p += 1
                continue
            try:
                d = json.loads(body)
            except Exception:
                print(f"{slug} page {p}: bad json; skipping", flush=True)
                p += 1
                continue
            if total_pages is None:
                total_pages = d.get("totalPages") or 0
                print(f"{slug}: total={d.get('total')} totalPages={total_pages}", flush=True)
            data = d.get("data", [])
            if not data:
                print(f"{slug} page {p}: empty; stopping", flush=True)
                break
            for r in data:
                c = code_of(r.get("link", ""))
                if not c or c in excl or c in seen:
                    continue
                seen.add(c)
                country = (r.get("country") or {}).get("iso2", "") or ""
                candidates.append({
                    "title": (r.get("group_title") or "").strip(),
                    "desc": (r.get("group_desc") or "").strip(),
                    "tags": r.get("tags") or [],
                    "code": c,
                    "country": country.upper() if len(country) == 2 else "",
                    "img": r.get("group_img") or "",
                    "category": canon,
                    "cat_slug": slug,
                })
            pages_done = p
            p += 1
            if total_pages and p > total_pages:
                break
        resume["pages_done"][slug] = pages_done
        print(f"{slug}: harvested {pages_done} pages, candidates so far {len(candidates)}", flush=True)
    json.dump({"candidates": candidates, "resume": resume}, open("/tmp/team07_candidates.json", "w"), ensure_ascii=False)
    print(f"DONE: {len(candidates)} fresh candidates saved", flush=True)

if __name__ == "__main__":
    main()
