#!/usr/bin/env python3
"""TEAM 01 wave 20261111 — curl-based slow verifier (total-time bounded).
Live check per task rules: curl https://chat.whatsapp.com/<code> with browser UA.
LIVE iff HTTP 200 AND non-empty og:title (retried once after a pause).
Runs SEQUENTIALLY (1 at a time, >=1s delay) — parallel fetches time out
through the shared egress proxy. curl --max-time bounds TOTAL time per check.
Usage: team01_verify_curl.py <candidates.json>  (merges with existing OUT files)
"""
import json, re, subprocess, sys, os, time, html

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
OUT_VER = os.path.join(WAVE, "team01-leads-slice1.json")
OUT_PEND = os.path.join(WAVE, "team01-leads-slice1-pending.json")
EXISTING_FILE = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)

SCAM_TOKENS = ["b-love","blove","b love","forsage","sheyi","holiverse","meta whale","metawhale",
    "1win","91club","91 club","aviator predictor","double money","investment plan"]
PORN_TOKENS = ["xxx","porn","sex video","sexy video","hot video","nude","desi sex","adult video",
    "blue film","porn video","sex group","xxx video","hot girls video","sex chat"]
NEG_RE = re.compile(r"[^.!?\n]*(?:no\s+(?:porn|xxx|sex|adult|nude)|porn\s+not\s+allowed|no\s+adult\s+content|strictly\s+no\s+porn)[^.!?\n]*[.!?]?", re.I)

def screen_text(text):
    t = (text or "").lower()
    t2 = NEG_RE.sub(" ", t)
    for tok in SCAM_TOKENS:
        if tok in t2: return f"scam:{tok}"
    for tok in PORN_TOKENS:
        if tok in t2: return f"adult:{tok}"
    return None

def load_json(path, default):
    try:
        with open(path) as f: return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f: json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)

def curl_check(code):
    """Returns (http_code, og_title, error). Total time bounded by --max-time 45."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        p = subprocess.run(
            ["curl", "-s", "--http1.1", "-A", UA, "--max-time", "45",
             "-w", "\n%{http_code}", url],
            capture_output=True, text=True, timeout=60)
        out = p.stdout
        lines = out.rsplit("\n", 1)
        body = lines[0] if len(lines) == 2 else out
        try:
            http = int(lines[1].strip()) if len(lines) == 2 else 0
        except ValueError:
            http = 0
        if p.returncode == 28:
            return (0, "", "transport:curl-timeout-45s")
        if p.returncode != 0:
            return (0, "", f"transport:curl-rc{p.returncode}")
        m = OG_RE.search(body)
        return (http, html.unescape(m.group(1)).strip() if m else "", "")
    except subprocess.TimeoutExpired:
        return (0, "", "transport:curl-subprocess-timeout")
    except Exception as e:
        return (0, "", f"transport:{type(e).__name__}")

def main():
    cand_path = sys.argv[1]
    cands = load_json(cand_path, {})
    # also accept a list of records with invite field
    if isinstance(cands, list):
        cands = {r["invite"].split("/")[-1]: r for r in cands if r.get("invite")}
    existing = set(load_json(EXISTING_FILE, []))
    verified = load_json(OUT_VER, [])
    pending_old = load_json(OUT_PEND, [])
    done_verified = {v["invite"].split("/")[-1] for v in verified}
    pending = []
    exclusions = []
    # pending codes are retried; verified codes skipped
    by_code = {}
    for code, rec in cands.items():
        if code not in existing and code not in done_verified:
            by_code[code] = rec
    for p in pending_old:
        code = p["invite"].split("/")[-1]
        if code not in done_verified and code not in by_code:
            by_code[code] = p
    items = list(by_code.items())
    print(f"curl-verify: {len(items)} to check", flush=True)
    dead = 0
    n = 0
    for code, rec in items:
        time.sleep(1.0)
        r = screen_text(rec.get("name", ""))
        if r:
            exclusions.append({"code": code, "reason": r + " (name)"})
            n += 1
            continue
        http, og, err = curl_check(code)
        if http == 200 and og:
            if screen_text(og):
                exclusions.append({"code": code, "reason": "adult/scam (og:title)"})
            else:
                verified.append({"name": (rec.get("name") or og)[:120], "category": rec.get("category", "Community & Social"),
                                 "country": rec.get("country", ""), "description": rec.get("description", ""),
                                 "invite": f"https://chat.whatsapp.com/{code}"})
        elif http == 200 and not og:
            time.sleep(3)
            http2, og2, err2 = curl_check(code)
            if http2 == 200 and og2:
                if screen_text(og2):
                    exclusions.append({"code": code, "reason": "adult/scam (og:title retry)"})
                else:
                    verified.append({"name": (rec.get("name") or og2)[:120], "category": rec.get("category", "Community & Social"),
                                     "country": rec.get("country", ""), "description": rec.get("description", ""),
                                     "invite": f"https://chat.whatsapp.com/{code}"})
            elif http2 == 200 and not og2:
                dead += 1
            else:
                pending.append({**{k: rec.get(k, "") for k in ("name", "category", "country", "description")},
                                "invite": f"https://chat.whatsapp.com/{code}", "reason": err2 or f"http_{http2}"})
        else:
            pending.append({**{k: rec.get(k, "") for k in ("name", "category", "country", "description")},
                            "invite": f"https://chat.whatsapp.com/{code}", "reason": err or f"http_{http}"})
        n += 1
        if n % 25 == 0:
            save_json(OUT_VER, verified); save_json(OUT_PEND, pending)
            print(f"  checked {n}/{len(items)}: live={len(verified)} pending={len(pending)} dead={dead} excl={len(exclusions)}", flush=True)
    save_json(OUT_VER, verified); save_json(OUT_PEND, pending)
    prog = load_json(os.path.join(WAVE, "team01-leads-slice1-progress.json"), {})
    prog["verify_dead"] = prog.get("verify_dead", 0) + dead
    prog["verify_exclusions"] = prog.get("verify_exclusions", []) + exclusions
    save_json(os.path.join(WAVE, "team01-leads-slice1-progress.json"), prog)
    print(f"CURL-VERIFY DONE: live={len(verified)} pending={len(pending)} dead_this_run={dead} excl_this_run={len(exclusions)}", flush=True)

if __name__ == "__main__":
    main()
