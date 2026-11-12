#!/usr/bin/env python3
"""TEAM 01 wave 20261112 — streaming verifier (fast live check).
Resume of wave_20261111 run2 (died at 525/1184 in a VM reboot; its dead list was
never persisted, so this run re-checks the merged file and PERSISTS dead codes
to team01-stream-dead.json, skipped on resume).
Reads only the first ~16KB of the WhatsApp invite page (og:title lives in <head>)
instead of downloading the whole ~220KB body, which trickles for minutes
through the shared egress proxy. Hard wall-clock deadline 40s per attempt.
Live = HTTP 200 + non-empty og:title, retried once after a pause.
SEQUENTIAL (1 at a time, >=1s delay). Writes SEPARATE stream outputs so it
never races the requests-based verifier: team01-stream-verified.json /
team01-stream-pending.json / team01-stream-dead.json
(+ dead/exclusion counts to team01-stream-stats.json).
Usage: team01_verify_stream.py <candidates.json>
"""
import json, re, sys, os, time, html
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
OUT_VER = os.path.join(WAVE, "team01-stream-verified.json")
OUT_PEND = os.path.join(WAVE, "team01-stream-pending.json")
OUT_DEAD = os.path.join(WAVE, "team01-stream-dead.json")
OUT_STATS = os.path.join(WAVE, "team01-stream-stats.json")
EXISTING_FILE = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
MAIN_VER = os.path.join(WAVE, "team01-leads-slice1.json")
MAIN_PEND = os.path.join(WAVE, "team01-leads-slice1-pending.json")
# normalize off-list categories mined yesterday into the allowed list
CATMAP = {"Buy Sell": "Buy & Sell", "Online Earning": "Finance", "Travel": "Community & Social"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
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

def is_junk_name(n):
    if not n or not n.strip():
        return True
    s = n.strip()
    if "<" in s or ">" in s:
        return True
    if s in {"Now", "NOW", "Link", "Links", "Group", "CHAT LINK", "Entrar no Grupo", "Join", "Join Group", "Join Now"}:
        return True
    if re.match(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$", s):
        return True
    if len(s) <= 2:
        return True
    return False

def bank_name(rec, og):
    """Banked name unless junk — then the authoritative og:title; None if both unusable."""
    nm = (rec.get("name") or "").strip()
    if not is_junk_name(nm):
        return nm[:120]
    ogc = (og or "").strip()
    if ogc and not is_junk_name(ogc):
        return ogc[:120]
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

_SESSION = None
def _sess():
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update(UA)
    return _SESSION

def head_check(code, deadline_s=60):
    """Fetch only the head of the invite page. Returns (http, og_title, err).
    Uses a persistent keep-alive session: fresh TLS per request costs ~10s
    on this VM, warm session requests ~3s (measured 20261112)."""
    url = f"https://chat.whatsapp.com/{code}"
    t0 = time.time()
    try:
        r = _sess().get(url, timeout=30, stream=True)
        if r.status_code != 200:
            r.close()
            return (r.status_code, "", f"http_{r.status_code}")
        buf = b""
        for chunk in r.iter_content(chunk_size=1024):
            buf += chunk
            m = OG_RE.search(buf.decode("utf-8", errors="ignore"))
            if m:
                r.close()
                return (200, html.unescape(m.group(1)).strip(), "")
            if len(buf) >= 16384:
                break
            if time.time() - t0 > deadline_s:
                break
        r.close()
        m = OG_RE.search(buf.decode("utf-8", errors="ignore"))
        if m:
            return (200, html.unescape(m.group(1)).strip(), "")
        if time.time() - t0 > deadline_s:
            return (0, "", "transport:head-deadline-60s")
        return (200, "", "")
    except Exception as e:
        global _SESSION
        try:
            _SESSION.close()
        except Exception:
            pass
        _SESSION = None
        return (0, "", f"transport:{type(e).__name__}")

def main():
    cand_path = sys.argv[1]
    cands = load_json(cand_path, {})
    if isinstance(cands, list):
        cands = {r["invite"].split("/")[-1]: r for r in cands if r.get("invite")}
    existing = set(load_json(EXISTING_FILE, []))
    main_verified = {v["invite"].split("/")[-1] for v in load_json(MAIN_VER, [])}
    stream_verified = load_json(OUT_VER, [])
    stream_pending = load_json(OUT_PEND, [])
    # exclusions are cumulative across passes (merged pass, then deep pass)
    exclusions = load_json(OUT_STATS, {}).get("exclusions", [])
    dead_codes = set(load_json(OUT_DEAD, []))
    done = main_verified | {v["invite"].split("/")[-1] for v in stream_verified} | dead_codes
    # (verify3 is finished, so its pending codes are retried here, not excluded)
    items = [(c, r) for c, r in cands.items()
             if c not in existing and c not in done]
    # dedupe preserving order
    seen = set(); todo = []
    for c, r in items:
        if c not in seen:
            seen.add(c); todo.append((c, r))
    dead = 0
    dead_list = sorted(dead_codes)
    print(f"stream-verify: {len(todo)} to check (skipping {len(dead_codes)} already-dead)", flush=True)
    n = 0
    for code, rec in todo:
        time.sleep(1.0)
        r = screen_text(rec.get("name", ""))
        if r:
            exclusions.append({"code": code, "reason": r + " (name)"})
            n += 1
            continue
        http, og, err = head_check(code)
        if http == 200 and og:
            if screen_text(og):
                exclusions.append({"code": code, "reason": "adult/scam (og:title)"})
            else:
                nm = bank_name(rec, og)
                if nm is None:
                    exclusions.append({"code": code, "reason": "no usable name (banked+og:title junk)"})
                else:
                    cat = CATMAP.get(rec.get("category", "Community & Social"), rec.get("category", "Community & Social"))
                    desc = rec.get("description", "") if not is_junk_name(rec.get("name", "")) else f"Join {nm}, an active WhatsApp group for {cat.lower()}. Connect with members, share updates and stay in touch."
                    stream_verified.append({"name": nm, "category": cat, "country": rec.get("country", ""),
                        "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
        elif http == 200 and not og:
            time.sleep(3)
            http2, og2, err2 = head_check(code)
            if http2 == 200 and og2:
                if screen_text(og2):
                    exclusions.append({"code": code, "reason": "adult/scam (og:title retry)"})
                else:
                    nm = bank_name(rec, og2)
                    if nm is None:
                        exclusions.append({"code": code, "reason": "no usable name (banked+og:title junk)"})
                    else:
                        cat = CATMAP.get(rec.get("category", "Community & Social"), rec.get("category", "Community & Social"))
                        desc = rec.get("description", "") if not is_junk_name(rec.get("name", "")) else f"Join {nm}, an active WhatsApp group for {cat.lower()}. Connect with members, share updates and stay in touch."
                        stream_verified.append({"name": nm, "category": cat, "country": rec.get("country", ""),
                            "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
            elif http2 == 200 and not og2:
                dead += 1; dead_list.append(code)
            else:
                stream_pending.append({**{k: rec.get(k, "") for k in ("name", "category", "country", "description")},
                    "invite": f"https://chat.whatsapp.com/{code}", "reason": err2 or f"http_{http2}"})
        else:
            stream_pending.append({**{k: rec.get(k, "") for k in ("name", "category", "country", "description")},
                "invite": f"https://chat.whatsapp.com/{code}", "reason": err or f"http_{http}"})
        n += 1
        if n % 10 == 0:
            save_json(OUT_VER, stream_verified); save_json(OUT_PEND, stream_pending)
            save_json(OUT_DEAD, sorted(set(dead_list)))
            save_json(OUT_STATS, {"dead": dead + len(dead_codes), "exclusions": exclusions, "checked": n, "total": len(todo)})
            print(f"  checked {n}/{len(todo)}: live={len(stream_verified)} pending={len(stream_pending)} dead={dead} excl={len(exclusions)}", flush=True)
    save_json(OUT_VER, stream_verified); save_json(OUT_PEND, stream_pending)
    save_json(OUT_DEAD, sorted(set(dead_list)))
    save_json(OUT_STATS, {"dead": dead + len(dead_codes), "exclusions": exclusions, "checked": n, "total": len(todo)})
    print(f"STREAM-VERIFY DONE: live={len(stream_verified)} pending={len(stream_pending)} dead={dead} excl={len(exclusions)}", flush=True)

if __name__ == "__main__":
    main()
