#!/usr/bin/env python3
"""team07: re-verify appgrouplink pending codes (wave 20261104 team18).
Checkpoint + incremental outputs live in the wave dir (NOT /tmp — /tmp gets cleared)."""
import json, re, html, random, subprocess, time, threading, os
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches"
PENDING_IN = f"{BASE}/wave_20261104/team18-unverified-pending.json"
UNION = f"{BASE}/wave_20261105/dedupe_union.json"
OUTDIR = f"{BASE}/wave_20261105"
CKPT = f"{OUTDIR}/team07-progress.jsonl"

BLOCK_RE = re.compile(
    r"(porn|xxx|xnxx|xvideo|pornhub|redtube|sex\s*video|nude|naked|escort|call\s*girl"
    r"|hyip|crypto\s*pump|satta|matka|double\s*(your|the)\s*money|money\s*mule"
    r"|counterfeit|buy\s+(cocaine|heroin|weed|drugs)|child\s*sex|teen\s*sex|cp\s*group)",
    re.I)
URL_NAME_RE = re.compile(r"(https?://|www\.|\.com|\.net|\.in\b)", re.I)
GENERIC_TITLES = {"whatsapp group invite", "join group chat on whatsapp", "whatsapp", "invite"}

def extract_code(invite):
    m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)", invite or "")
    return m.group(1) if m else None

def fetch_og_title(code):
    try:
        p = subprocess.run(
            ["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "20",
             "-w", "\n%{http_code}", f"https://chat.whatsapp.com/{code}"],
            capture_output=True, text=True, timeout=30)
        out = p.stdout
        lines = out.rsplit("\n", 1)
        http_code = lines[1].strip() if len(lines) == 2 else "000"
        body = lines[0]
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body, re.I)
        title = html.unescape(m.group(1)).strip() if m else ""
        return http_code, title
    except Exception:
        return "ERR", ""

def classify(rec, code, title):
    name = (rec.get("name") or "").strip()
    if not name:
        name = title
    blob = f"{name} {title}"
    if URL_NAME_RE.search(name) or BLOCK_RE.search(blob):
        return {"code": code, "name": name, "note": f"blocked content (og:title={title!r})", "status": "drop"}
    return {"code": code, "name": name, "note": "", "status": "verified",
            "record": {"name": name, "category": rec.get("category", ""),
                       "country": rec.get("country", "International"),
                       "description": rec.get("description", ""),
                       "invite": f"https://chat.whatsapp.com/{code}",
                       "image": rec.get("image", "") or ""}}

def write_outputs(done, pending):
    verified, pend, drops = [], [], 0
    for code, r in done.items():
        if r["status"] == "verified":
            verified.append(r["record"])
        elif r["status"] == "pending":
            pend.append({"code": code, "name": r.get("name", ""), "note": r.get("note", "")})
        else:
            drops += 1
    for rec in pending:
        code = extract_code(rec.get("invite", ""))
        if code and code not in done:
            pend.append({"code": code, "name": rec.get("name", ""), "note": "not-attempted: run stopped early"})
    verified.sort(key=lambda r: r["name"].lower())
    tmp = f"{OUTDIR}/team07-appgrouplink.json.tmp"
    json.dump(verified, open(tmp, "w"), ensure_ascii=False, indent=2); os.replace(tmp, f"{OUTDIR}/team07-appgrouplink.json")
    tmp = f"{OUTDIR}/team07-unverified-pending.json.tmp"
    json.dump(pend, open(tmp, "w"), ensure_ascii=False, indent=2); os.replace(tmp, f"{OUTDIR}/team07-unverified-pending.json")
    json.dump([], open(f"{OUTDIR}/team07-leads.json", "w"))
    return len(verified), len(pend), drops

def main():
    pending = json.load(open(PENDING_IN))
    union = set(json.load(open(UNION)))
    print(f"loaded pending={len(pending)} union={len(union)}", flush=True)

    done = {}
    try:
        with open(CKPT) as f:
            for line in f:
                r = json.loads(line)
                done[r["code"]] = r
    except FileNotFoundError:
        pass
    print(f"resuming with {len(done)} already processed", flush=True)

    lock = threading.Lock()
    ckpt_f = open(CKPT, "a")
    stop_flag = threading.Event()
    consec_429 = {"n": 0}
    counter = {"n": len(done)}

    def process(rec):
        if stop_flag.is_set():
            return None
        invite = rec.get("invite", "")
        code = extract_code(invite)
        if not code:
            return {"code": "", "name": rec.get("name", ""), "note": "bad-invite-url", "status": "drop"}
        with lock:
            if code in done:
                return done[code]
        if code in union:
            res = {"code": code, "name": rec.get("name", ""), "note": "in-union", "status": "drop"}
        elif "/channel/" in invite:
            res = {"code": code, "name": rec.get("name", ""), "note": "channel-excluded", "status": "drop"}
        else:
            time.sleep(random.uniform(0.5, 2.0))
            http_code, title = fetch_og_title(code)
            if http_code == "429":
                with lock:
                    consec_429["n"] += 1
                    n = consec_429["n"]
                print(f"429 on {code} (consec={n}) — backing off 180s", flush=True)
                time.sleep(180)
                if n >= 8:
                    stop_flag.set()
                    res = {"code": code, "name": rec.get("name", ""), "note": "rate-limited", "status": "pending"}
                else:
                    time.sleep(random.uniform(0.5, 2.0))
                    http_code, title = fetch_og_title(code)
                    if http_code == "429" or not title:
                        res = {"code": code, "name": rec.get("name", ""), "note": "rate-limited", "status": "pending"}
                    else:
                        res = classify(rec, code, title)
            else:
                with lock:
                    consec_429["n"] = 0
                if not title:
                    res = {"code": code, "name": rec.get("name", ""), "note": f"empty-og-title (http {http_code})", "status": "pending"}
                else:
                    res = classify(rec, code, title)
        with lock:
            done[code] = res
            ckpt_f.write(json.dumps(res) + "\n"); ckpt_f.flush()
            counter["n"] += 1
            if counter["n"] % 100 == 0:
                v, p, d = write_outputs(done, pending)
                print(f"checkpoint {counter['n']}/1354 verified={v} pending={p} drops={d}", flush=True)
        return res

    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(process, pending))

    ckpt_f.close()
    v, p, d = write_outputs(done, pending)
    print(f"ATTEMPTED={len(done)} VERIFIED={v} PENDING={p} DROPS={d}", flush=True)

if __name__ == "__main__":
    main()
