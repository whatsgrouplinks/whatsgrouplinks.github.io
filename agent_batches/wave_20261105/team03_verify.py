#!/usr/bin/env python3
"""team03 — re-verify igrupos pending codes (wave 20261104 team35, 3,183 records).
Control test PASSED with full Chrome UA: known-live code KrDwdK8EIkB6vgauHg5M7N
returned HTTP 200 + og:title 'JAY - PHP & Python Full Stack Developer'.
(Bare 'Mozilla/5.0' UA returns an empty body — WhatsApp blocks it; full UA required.)
Bogus code returns HTTP 200 with EMPTY og:title, so non-empty og:title = live group.

Method per candidate: curl -sL -A <full Chrome UA> --max-time 20, read only first
64KB of body (og:title sits ~2.5KB in), parse og:title + HTTP code from -D headers.
Max 4 workers, random 0.5-1.5s delay per worker between requests.
On HTTP 429: global backoff (180s, doubling to max 900s), all workers pause.
Checkpoint: team03-progress.jsonl (one line per attempted code) — resume-safe.
"""
import json, re, os, random, subprocess, threading, time, html, sys
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105"
PENDING_SRC = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team35-unverified-pending.json"
UNION = os.path.join(BASE, "dedupe_union.json")
PROGRESS = os.path.join(BASE, "team03-progress.jsonl")
OUT_VERIFIED = os.path.join(BASE, "team03-igrupos.json")
OUT_PENDING = os.path.join(BASE, "team03-unverified-pending.json")
OUT_LEADS = os.path.join(BASE, "team03-leads.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)")
GENERIC_TITLES = {"", "whatsapp group invite", "whatsapp", "whatsapp group"}

# Hard content blocks decided from pre-verification review (see report):
#  - DmuCwu9Ewly9Ufr0TyPlex 'NEXXX FREE' — xxx/free porn slug
#  - IPqkyHCH6Sp9fja6EW3aq6 'Amistades' desc 'Muestra tetas su ropa interior...' — group solicits nude/underwear photos
HARD_DROPS = {
    "DmuCwu9Ewly9Ufr0TyPlex": "dropped: hard block — xxx/free porn slug (NEXXX FREE)",
    "IPqkyHCH6Sp9fja6EW3aq6": "dropped: hard block — description solicits nude/underwear photos",
}
# Post-verification og:title blocks (porn/scam signals in the LIVE title)
OG_BLOCK_RES = [
    re.compile(p, re.I) for p in [
        r"porn", r"onlyfans", r"escort", r"call\s*girl", r"satta", r"xxx\s*(free|video|porn|sex)",
        r"free\s*xxx", r"sex\s*video", r"porno", r"sexo\s*gratis", r"crypto\s*pump",
        r"pump\s*signal", r"hyip", r"money\s*mule",
    ]
]

COUNTRY_NAMES = {
    "MX": "Mexico", "CO": "Colombia", "VE": "Venezuela", "PE": "Peru", "DO": "Dominican Republic",
    "EC": "Ecuador", "CL": "Chile", "GT": "Guatemala", "UY": "Uruguay", "BO": "Bolivia",
    "AR": "Argentina", "PY": "Paraguay", "HN": "Honduras", "SV": "El Salvador", "NI": "Nicaragua",
    "CR": "Costa Rica", "PA": "Panama", "CU": "Cuba", "ES": "Spain", "US": "United States",
    "BR": "Brazil",
}

# ---- 429 backoff state ----
backoff_lock = threading.Lock()
backoff_until = [0.0]
backoff_secs = [180.0]
progress_lock = threading.Lock()
attempted = {}   # code -> result dict (loaded from checkpoint)
n_done = [0]

def log_progress(rec):
    with progress_lock:
        with open(PROGRESS, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def wait_backoff():
    while True:
        with backoff_lock:
            until = backoff_until[0]
        now = time.time()
        if now >= until:
            return
        time.sleep(min(10, until - now))

def trigger_backoff():
    with backoff_lock:
        backoff_until[0] = time.time() + backoff_secs[0]
        print(f"[{time.strftime('%H:%M:%S')}] HTTP 429 — backing off {backoff_secs[0]:.0f}s", flush=True)
        backoff_secs[0] = min(backoff_secs[0] * 2, 900.0)

def verify_code(code, worker_id):
    """Returns dict with status: verified|pending, og_title, http code, note."""
    url = f"https://chat.whatsapp.com/{code}"
    hdr = f"/tmp/team03_h_{worker_id}.txt"
    try:
        proc = subprocess.Popen(
            ["curl", "-sL", "-A", UA, "--max-time", "20", "-D", hdr, url],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            chunk = proc.stdout.read(65536)
        except Exception:
            chunk = b""
        finally:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                proc.wait(timeout=5)
            except Exception:
                pass
    except Exception as e:
        return {"status": "pending", "og_title": "", "http": 0, "note": f"curl error: {e}"}
    http_code = 0
    try:
        with open(hdr, "r", errors="ignore") as f:
            for line in f:
                m = re.match(r"HTTP/\S+\s+(\d+)", line)
                if m:
                    http_code = int(m.group(1))
    except Exception:
        pass
    if http_code == 429:
        trigger_backoff()
        return {"status": "pending", "og_title": "", "http": 429,
                "note": "http-429 rate-limited — backed off; retry next wave"}
    text = chunk.decode("utf-8", errors="ignore")
    m = OG_RE.search(text)
    og = html.unescape(m.group(1)).strip() if m else ""
    if og and og.lower() not in GENERIC_TITLES:
        for rx in OG_BLOCK_RES:
            if rx.search(og):
                return {"status": "dropped", "og_title": og, "http": http_code,
                        "note": f"dropped: hard block — live og:title matched {rx.pattern!r}"}
        return {"status": "verified", "og_title": og, "http": http_code, "note": ""}
    if http_code == 0:
        note = "curl timeout/error — no HTTP response; retry next wave"
    elif http_code != 200:
        note = f"http-{http_code} — empty og:title; retry next wave"
    else:
        note = "empty og:title (HTTP 200) — group dead, renamed, invite revoked or invalid"
    return {"status": "pending", "og_title": og, "http": http_code, "note": note}

def looks_mojibake(name):
    # double-encoded UTF-8 artefacts typical of the previous wave's scrape
    return ("Ã" in name) or ("â" in name) or ("ð" in name and "Ÿ" in name) or ("ð" in name and "ð" in name)

def clean_name(listed, og):
    if not listed:
        return og
    if looks_mojibake(listed):
        return og if og else listed
    # emoji/symbol-only name with no letters -> prefer live title
    if og and not re.search(r"[A-Za-zÀ-ÿ0-9]", listed):
        return og
    return listed

def make_description(name, category, country):
    cname = COUNTRY_NAMES.get(country, country if country else "International")
    cat = (category or "Other").strip()
    if cat.lower() == "other":
        return (f"Join {name}, an active WhatsApp group and community in {cname}. "
                f"Chat, share and connect with members from {cname}.")
    return (f"Join {name}, an active WhatsApp group for {cat} fans in {cname}. "
            f"Chat, share and connect with members who love {cat}.")

def main():
    union = set(json.load(open(UNION, encoding="utf-8")))
    src = json.load(open(PENDING_SRC, encoding="utf-8"))
    print(f"loaded: union={len(union)} pending-src={len(src)}", flush=True)
    if os.path.exists(PROGRESS):
        with open(PROGRESS, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    attempted[r["code"]] = r
                except Exception:
                    pass
    print(f"checkpoint: already attempted={len(attempted)}", flush=True)

    todo = []
    stats = {"in_union": 0, "dropped_pre": 0, "skipped_done": 0}
    for rec in src:
        invite = rec.get("invite", "")
        m = CODE_RE.search(invite)
        if not m:
            continue
        code = m.group(1)
        if code in union:
            stats["in_union"] += 1
            continue
        if code in HARD_DROPS:
            r = {"code": code, "name": rec.get("name", ""), "status": "dropped",
                 "og_title": "", "http": 0, "note": HARD_DROPS[code]}
            attempted[code] = r
            log_progress(r)
            stats["dropped_pre"] += 1
            continue
        if code in attempted:
            stats["skipped_done"] += 1
            continue
        todo.append((code, rec))
    print(f"todo={len(todo)} in_union={stats['in_union']} dropped_pre={stats['dropped_pre']} "
          f"skipped_done={stats['skipped_done']}", flush=True)

    def worker(item, wid):
        code, rec = item
        wait_backoff()
        res = verify_code(code, wid)
        res.update({"code": code, "name": rec.get("name", "")})
        with progress_lock:
            attempted[code] = res
            n_done[0] += 1
            if n_done[0] % 100 == 0:
                v = sum(1 for r in attempted.values() if r.get("status") == "verified")
                p = sum(1 for r in attempted.values() if r.get("status") == "pending")
                d = sum(1 for r in attempted.values() if r.get("status") == "dropped")
                print(f"[{time.strftime('%H:%M:%S')}] attempted={len(attempted)} "
                      f"verified={v} pending={p} dropped={d} todo-left={len(todo)-n_done[0]}", flush=True)
        log_progress(res)
        time.sleep(random.uniform(0.5, 1.5))

    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = []
        for i, item in enumerate(todo):
            wid = i % 4
            futs.append(ex.submit(worker, item, wid))
        for f in futs:
            f.result()
    print("verification pass complete", flush=True)
    build_outputs(src)
    v = sum(1 for r in attempted.values() if r.get("status") == "verified")
    p = sum(1 for r in attempted.values() if r.get("status") == "pending")
    d = sum(1 for r in attempted.values() if r.get("status") == "dropped")
    print(f"FINAL attempted={len(attempted)} verified={v} pending={p} dropped={d}", flush=True)

def build_outputs(src):
    by_code = {}
    for rec in src:
        m = CODE_RE.search(rec.get("invite", ""))
        if m:
            by_code[m.group(1)] = rec
    verified, pending = [], []
    for code, r in attempted.items():
        rec = by_code.get(code)
        if rec is None:
            continue
        if r.get("status") == "verified":
            name = clean_name((rec.get("name") or "").strip(), r.get("og_title", ""))
            category = (rec.get("category") or "Other").strip() or "Other"
            country = (rec.get("country") or "International").strip() or "International"
            desc = (rec.get("description") or "").strip()
            if not desc or "igrupos" in desc.lower() or "http" in desc.lower():
                desc = make_description(name, category, country)
            image = rec.get("image") or ""
            if image and not str(image).startswith("http"):
                image = ""
            verified.append({
                "name": name, "category": category, "country": country,
                "description": desc,
                "invite": f"https://chat.whatsapp.com/{code}", "image": image,
            })
        elif r.get("status") == "pending":
            pending.append({"code": code, "name": rec.get("name", ""),
                            "note": r.get("note", "pending")})
    verified.sort(key=lambda x: x["name"].lower())
    pending.sort(key=lambda x: x["code"])
    with open(OUT_VERIFIED, "w", encoding="utf-8") as f:
        json.dump(verified, f, ensure_ascii=False, indent=2)
    with open(OUT_PENDING, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)
    with open(OUT_LEADS, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    print(f"wrote {OUT_VERIFIED} ({len(verified)})", flush=True)
    print(f"wrote {OUT_PENDING} ({len(pending)})", flush=True)
    print(f"wrote {OUT_LEADS} (0)", flush=True)

if __name__ == "__main__":
    main()
