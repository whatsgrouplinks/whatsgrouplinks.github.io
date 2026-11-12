#!/usr/bin/env python3
"""TEAM 10 — WhatsGroupLinks wave 20261111, leads slice 5 (linkado.app).
Phase A: fetch each listing page (curl, browser UA), extract invite codes + name/category/desc.
Phase B: slow-verify each NEW code (curl chat.whatsapp.com, max 6 workers, >=0.5s delay,
retry once after pause on empty og:title). LIVE iff HTTP 200 AND non-empty og:title.
Resumable via JSONL checkpoints. Writes only into the wave dir.
"""
import json, re, subprocess, sys, time, threading, html, os
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
LEADS = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/leads_slice5.json"
EXISTING = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
MINE_CKPT = os.path.join(WAVE, "team10-mine-checkpoint.jsonl")
VERIFY_CKPT = os.path.join(WAVE, "team10-verify-checkpoint.jsonl")
PROGRESS = os.path.join(WAVE, "team10-progress.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
MINE_WORKERS = 32
VERIFY_WORKERS = 6

lock = threading.RLock()  # RLock: save_progress() is called from inside locked sections
progress = {"phase": "mine", "mined": 0, "verified": 0, "started": time.strftime("%Y-%m-%d %H:%M:%S")}

def save_progress():
    with lock:
        tmp = PROGRESS + ".tmp"
        with open(tmp, "w") as f:
            json.dump(progress, f, indent=1)
        os.replace(tmp, PROGRESS)

def append_ckpt(path, rec):
    with lock:
        with open(path, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def load_ckpt_urls(path):
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    done.add(json.loads(line)["url"])
                except Exception:
                    pass
    return done

def load_ckpt_codes(path):
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    done.add(json.loads(line)["code"])
                except Exception:
                    pass
    return done

def curl(url, max_time=45):
    """Returns (http_code:int|0, body:str, ok:bool). ok=False on curl failure."""
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "-A", UA, "--max-time", str(max_time),
             "-w", "\n__HTTP__%{http_code}", url],
            capture_output=True, text=True, timeout=max_time + 15)
        out = r.stdout
        m = re.search(r"\n__HTTP__(\d{3})\s*$", out)
        code = int(m.group(1)) if m else 0
        body = out[:m.start()] if m else out
        return code, body, (r.returncode == 0 and code != 0)
    except Exception:
        return 0, "", False

TITLE_RE = re.compile(r"<title>\s*Grupo de WhatsApp\s+(.*)\s*-\s*([^<]+?)\s*</title>", re.S | re.I)
OGTITLE_RE = re.compile(r'property="og:title"\s+content="([^"]*)"', re.I)
OGDESC_RE = re.compile(r'property="og:description"\s+content="([^"]*)"', re.I)
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})")

def parse_listing(html_body):
    name, cat_pt, desc = "", "", ""
    m = TITLE_RE.search(html_body)
    if m:
        name = html.unescape(m.group(1)).strip()
        cat_pt = html.unescape(m.group(2)).strip()
    else:
        m2 = OGTITLE_RE.search(html_body)
        if m2:
            t = html.unescape(m2.group(1)).strip()
            t = re.sub(r"^Grupo de WhatsApp\s+", "", t, flags=re.I)
            if " - " in t:
                name, cat_pt = t.rsplit(" - ", 1)
                name, cat_pt = name.strip(), cat_pt.strip()
            else:
                name = t
    d = OGDESC_RE.search(html_body)
    if d:
        raw = html.unescape(d.group(1)).strip()
        # "Grupo de WhatsApp NAME, na categoria CAT. <desc>"
        mm = re.search(r"na categoria [^.]*\.\s*(.*)$", raw, re.S)
        desc = mm.group(1).strip() if mm else raw
        desc = re.sub(r"^Grupo de WhatsApp\s+", "", desc)
    codes = sorted(set(CODE_RE.findall(html_body)))
    return name, cat_pt, desc, codes

def mine_one(url):
    last_code, last_err = 0, ""
    body = ""
    for attempt in range(3):
        code, body, ok = curl(url, max_time=45)
        last_code = code
        if ok and code == 200 and body:
            name, cat_pt, desc, codes = parse_listing(body)
            return {"url": url, "status": "ok", "http": code,
                    "name": name, "cat_pt": cat_pt, "desc": desc,
                    "codes": codes, "attempts": attempt + 1}
        if code == 429:
            time.sleep(30)
        elif code in (500, 502, 503, 504):
            time.sleep(10)
        else:
            time.sleep(5)
        last_err = f"http={code} ok={ok} len={len(body)}"
    if last_code in (404, 410):
        return {"url": url, "status": "http-404", "http": last_code, "attempts": 3}
    return {"url": url, "status": "fetch-failed", "http": last_code,
            "error": last_err, "attempts": 3}

def phase_mine(urls):
    done = load_ckpt_urls(MINE_CKPT)
    todo = [u for u in urls if u not in done]
    print(f"[mine] total={len(urls)} done={len(done)} todo={len(todo)}", flush=True)
    progress["phase"] = "mine"
    progress["mine_total"] = len(urls)
    progress["mined"] = len(done)
    save_progress()
    counter = {"n": 0}
    def work(url):
        rec = mine_one(url)
        append_ckpt(MINE_CKPT, rec)
        time.sleep(0.3)
        with lock:
            counter["n"] += 1
            progress["mined"] = len(done) + counter["n"]
            if counter["n"] % 50 == 0:
                save_progress()
                print(f"[mine] {progress['mined']}/{len(urls)}", flush=True)
        return rec
    with ThreadPoolExecutor(MINE_WORKERS) as ex:
        list(ex.map(work, todo))
    save_progress()
    print("[mine] complete", flush=True)

WA_TITLE_RE = re.compile(r'<meta property="og:title"\s+content="([^"]*)"', re.I)

def verify_one(code):
    """Returns record. Live iff http 200 and non-empty og:title (after 1 retry)."""
    url = f"https://chat.whatsapp.com/{code}"
    og = ""
    http = 0
    transport_fail = False
    for attempt in range(2):
        c, body, ok = curl(url, max_time=30)
        http = c
        if not ok:
            transport_fail = True
            time.sleep(5)
            continue
        transport_fail = False
        m = WA_TITLE_RE.search(body)
        og = html.unescape(m.group(1)).strip() if m else ""
        if og:
            break
        # empty og:title -> spaced retry once
        if attempt == 0:
            time.sleep(5)
    if transport_fail:
        return {"url": url, "code": code, "status": "pending",
                "reason": "transport failure after retries", "http": http, "og_title": og}
    if http == 200 and og:
        return {"url": url, "code": code, "status": "live", "http": http, "og_title": og}
    if http in (429, 500, 502, 503, 504):
        return {"url": url, "code": code, "status": "pending",
                "reason": f"http {http}", "http": http, "og_title": og}
    return {"url": url, "code": code, "status": "dead",
            "reason": f"http {http} empty-og={not og}", "http": http, "og_title": og}

def collect_codes():
    """Unique codes from mine checkpoint, minus existing codes."""
    existing = set(json.load(open(EXISTING)))
    seen = {}
    if os.path.exists(MINE_CKPT):
        with open(MINE_CKPT) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("status") != "ok":
                    continue
                for c in rec.get("codes", []):
                    if c not in seen:
                        seen[c] = rec
    new_codes = {c: r for c, r in seen.items() if c not in existing}
    return seen, new_codes

def phase_verify():
    seen, new_codes = collect_codes()
    done = load_ckpt_codes(VERIFY_CKPT)
    todo = [c for c in new_codes if c not in done]
    print(f"[verify] candidates={len(seen)} new={len(new_codes)} done={len(done)} todo={len(todo)}", flush=True)
    progress["phase"] = "verify"
    progress["verify_total"] = len(new_codes)
    progress["verified"] = len(done)
    save_progress()
    counter = {"n": 0}
    def work(code):
        rec = verify_one(code)
        append_ckpt(VERIFY_CKPT, rec)
        time.sleep(0.5)
        with lock:
            counter["n"] += 1
            progress["verified"] = len(done) + counter["n"]
            if counter["n"] % 50 == 0:
                save_progress()
                print(f"[verify] {progress['verified']}/{len(new_codes)}", flush=True)
        return rec
    with ThreadPoolExecutor(VERIFY_WORKERS) as ex:
        list(ex.map(work, todo))
    save_progress()
    print("[verify] complete", flush=True)

def main():
    urls = json.load(open(LEADS))
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "mine"):
        phase_mine(urls)
    if which in ("all", "verify"):
        phase_verify()
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
