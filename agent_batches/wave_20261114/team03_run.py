#!/usr/bin/env python3
"""team03 wave_20261114: linkado grupo sitemap indices 9000-10999 (+41 retry leads)."""
import json, re, time, html, random, unicodedata, os, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

_thread_local = threading.local()

def get_session():
    s = getattr(_thread_local, "session", None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _thread_local.session = s
    return s

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
W13 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
W10 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UNION = json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"))
UNION_SET = set(UNION)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

leads13 = json.load(open(f"{W13}/team34-leads.json"))
MAIN_URLS = [x["value"] for x in leads13 if "unmined" in x["note"]]
RETRY_URLS = [x["value"] for x in leads13 if "unmined" not in x["note"]]
assert len(MAIN_URLS) == 2000, len(MAIN_URLS)
ALL_URLS = MAIN_URLS + RETRY_URLS

RAW_F = f"{BASE}/team03-raw.json"
VER_F = f"{BASE}/team03-verify.json"

def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def fetch_one(args):
    i, url = args
    try:
        s = get_session()
        r = s.get(url, timeout=30)
        if r.status_code != 200:
            return {"idx": i, "url": url, "status": f"http{r.status_code}", "name": None, "code": None, "dircat": None}
        h = r.text
        m = re.search(r'"@type":"WebPage","name":"((?:[^"\\]|\\.)*)"', h)
        name = html.unescape(m.group(1)) if m else None
        if not name:
            t = re.search(r"<title>(.*?)</title>", h, re.S)
            if t:
                name = html.unescape(t.group(1))
                name = re.sub(r"^Grupo de WhatsApp\s+", "", name)
                name = re.sub(r"\s+-\s+[^-]+$", "", name)
        codes = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", h)
        code = codes[0] if codes else None
        dm = re.search(r"categoria de grupos de WhatsApp de ([^ ]+)", h)
        dircat = dm.group(1) if dm else None
        if not dircat:
            t = re.search(r"<title>Grupo de WhatsApp .*? - ([^<]+)</title>", h)
            dircat = t.group(1).strip() if t else None
        return {"idx": i, "url": url, "status": "ok", "name": name, "code": code, "dircat": dircat}
    except Exception as e:
        return {"idx": i, "url": url, "status": f"err:{type(e).__name__}", "name": None, "code": None, "dircat": None}

def load_json(path, default):
    if os.path.exists(path):
        return json.load(open(path))
    return default

def phase_fetch():
    done = {r["idx"]: r for r in load_json(RAW_F, [])}
    todo = [(i, u) for i, u in enumerate(ALL_URLS) if i not in done]
    print(f"fetch: {len(done)} done, {len(todo)} todo", flush=True)
    results = list(done.values())
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_one, a): a for a in todo}
        n = 0
        for f in as_completed(futs):
            results.append(f.result())
            n += 1
            if n % 100 == 0:
                results_sorted = sorted(results, key=lambda r: r["idx"])
                json.dump(results_sorted, open(RAW_F, "w"), ensure_ascii=False)
                print(f"fetch progress {len(results)}/{len(ALL_URLS)}", flush=True)
            time.sleep(0.02)
    results = sorted(results, key=lambda r: r["idx"])
    json.dump(results, open(RAW_F, "w"), ensure_ascii=False)
    print("fetch done", len(results), flush=True)
    return results

OG_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)

def verify_one(code):
    """Returns (status, title): status in live/dead/pending."""
    title = ""
    last_err = ""
    for attempt in range(3):
        try:
            s = get_session()
            r = s.get(f"https://chat.whatsapp.com/{code}", timeout=60)
            if r.status_code == 429:
                return ("pending", "", "http429")
            if r.status_code != 200:
                last_err = f"http{r.status_code}"
                time.sleep(5 * (attempt + 1))
                continue
            m = OG_RE.search(r.text)
            title = html.unescape(m.group(1)).strip() if m else ""
            if title and title not in ("WhatsApp Group Invite", "WhatsApp"):
                return ("live", title, "")
            if title in ("WhatsApp Group Invite", "WhatsApp"):
                return ("dead", title, "generic-title")
            last_err = "empty-title"
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            last_err = f"{type(e).__name__}"
            time.sleep(5 * (attempt + 1))
    if "429" in last_err or "Timeout" in last_err or "Connection" in last_err:
        return ("pending", "", last_err)
    return ("dead", "", last_err)

def phase_verify(raw):
    done = {v["code"]: v for v in load_json(VER_F, [])}
    # fresh codes: have code, not in union, first occurrence in team
    seen = set()
    todo = []
    dupes = 0
    for r in raw:
        c = r.get("code")
        if not c:
            continue
        if c in UNION_SET or c in seen:
            dupes += 1
            continue
        seen.add(c)
        if c not in done:
            todo.append(c)
    print(f"verify: {len(todo)} to check, {len(done)} already done, {dupes} dupes vs union/within-team", flush=True)
    results = list(done.values())
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(verify_one, c): c for c in todo}
        n = 0
        for f in as_completed(futs):
            code = futs[f]
            st, title, err = f.result()
            results.append({"code": code, "status": st, "title": title, "err": err})
            n += 1
            if n % 50 == 0:
                json.dump(results, open(VER_F, "w"), ensure_ascii=False)
                print(f"verify progress {n}/{len(todo)}", flush=True)
    json.dump(results, open(VER_F, "w"), ensure_ascii=False)
    print("verify done", flush=True)
    return results, dupes

if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    raw = phase_fetch() if phase in ("all", "fetch") else load_json(RAW_F, [])
    if phase in ("all", "verify"):
        phase_verify(raw)
    print("OK", phase)
