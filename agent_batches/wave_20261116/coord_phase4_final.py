#!/usr/bin/env python3
"""Wave 20261116 — PHASE 4 (final assembly).
Reads final verdicts (pass1/pass1b/retry429/pass2), screens live og:titles,
assembles clean / pending / excluded outputs + spot-check + manifest.
Run AFTER phase 3b finishes.
"""
import json, os, re, random, time, html, threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import requests
import importlib.util

BASE = "/home/hatch/workspace/whatsapp-groups-site"
OUT = os.path.join(BASE, "agent_batches/wave_20261116")

spec = importlib.util.spec_from_file_location("p4", os.path.join(OUT, "coord_phase4.py"))
p4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p4)
screen_title = p4.screen_title

GENERIC = {"", "whatsapp group invite", "whatsapp", "join group on whatsapp",
           "whatsapp group", "invite", "group invite"}
TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
_tls = threading.local()

def load_results(*paths):
    out = {}
    for p in paths:
        if os.path.exists(p):
            for line in open(p, encoding='utf-8'):
                try:
                    r = json.loads(line)
                    out[r["code"]] = r
                except Exception:
                    pass
    return out

def fetch_title(code):
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        _tls.s = s
    try:
        r = s.get("https://chat.whatsapp.com/" + code, headers=UA, timeout=30, stream=True)
        if r.status_code == 429:
            r.close(); return ("pending", "")
        body = b""
        for chunk in r.iter_content(chunk_size=8192):
            body += chunk
            if len(body) >= 49152:
                break
        r.close()
        m = TITLE_RE.search(body.decode('utf-8', 'ignore'))
        title = html.unescape(m.group(1)).strip() if m else ""
        if title and title.lower() not in GENERIC:
            return ("live", title)
        return ("dead", "")
    except Exception as e:
        return ("pending", f"{type(e).__name__}")

def main():
    queue = json.load(open(os.path.join(OUT, "verify_queue.json"), encoding='utf-8'))
    qmap = {q["code"]: q for q in queue}
    accepted = json.load(open(os.path.join(OUT, "accepted_team_live.json"), encoding='utf-8'))
    state = json.load(open(os.path.join(OUT, "phase1_state.json"), encoding='utf-8'))
    team_live = state["team_live"]
    excluded = json.load(open(os.path.join(OUT, "excluded_phase2.json"), encoding='utf-8'))
    excl_counts = Counter(e["reason"] for e in excluded)

    # final verdicts: live wins; else pending if any pending remains; else dead
    res = load_results(os.path.join(OUT, "verify_pass1.jsonl"),
                       os.path.join(OUT, "verify_pass1b.jsonl"))
    retry = load_results(os.path.join(OUT, "verify_retry429.jsonl"))
    p2 = load_results(os.path.join(OUT, "verify_pass2.jsonl"))
    # merge with precedence: pass2 > retry > pass1
    final = dict(res)
    for src in (retry, p2):
        for code, r in src.items():
            prev = final.get(code)
            if prev is None:
                final[code] = r
            elif r["status"] == "live":
                final[code] = r
            elif prev["status"] == "pending" and r["status"] in ("live", "empty"):
                final[code] = r
            elif prev["status"] == "empty" and r["status"] == "live":
                final[code] = r
    print("final verdicts:", len(final), Counter(r["status"] for r in final.values()))

    clean = []
    pending = []
    stats = Counter()
    # 1. team-live accepted, re-screened by og:title
    for rec in accepted:
        title = team_live.get(rec["code"].lower(), "")
        flag = screen_title(title) if title else None
        if flag:
            excluded.append({"code": rec["code"], "name": rec["name"], "team": rec["team"],
                             "reason": flag, "note": "via live og:title: " + title[:80]})
            excl_counts[flag] += 1
            stats["team-live-title-excluded"] += 1
            continue
        clean.append(finish_record(rec, title))
        stats["clean-team-live"] += 1
    # 2. my-verified queue
    for code, q in qmap.items():
        r = final.get(code)
        if r is None:
            pending.append({"code": code, "name": q["name"], "team": q["team"],
                            "reason": "never fetched (verifier incomplete)"})
            stats["pending-never-fetched"] += 1
            continue
        if r["status"] == "live":
            title = r["title"]
            flag = screen_title(title) or screen_title(q["name"])
            if flag:
                excluded.append({"code": code, "name": q["name"], "team": q["team"],
                                 "reason": flag, "note": "via live og:title: " + title[:80]})
                excl_counts[flag] += 1
                stats["verified-title-excluded"] += 1
                continue
            rec = dict(q)
            if not rec["name"]:
                rec["name"] = title
            clean.append(finish_record(rec, title))
            stats["clean-verified"] += 1
        elif r["status"] == "pending":
            pending.append({"code": code, "name": q["name"], "team": q["team"],
                            "reason": r.get("err") or "pending"})
            stats["pending"] += 1
        else:  # empty/dead
            excluded.append({"code": code, "name": q["name"], "team": q["team"],
                             "reason": "dead"})
            excl_counts["dead"] += 1
            stats["dead"] += 1

    print("stats:", dict(stats))
    print("clean total:", len(clean), "| pending:", len(pending), "| excluded total:", len(excluded))
    print("excluded by reason:", dict(excl_counts))

    # dedupe clean defensively (should already be unique)
    seen = set(); ded = []
    for rec in clean:
        k = rec["invite"].lower()
        if k in seen:
            continue
        seen.add(k); ded.append(rec)
    print("clean after defensive dedupe:", len(ded), "(dropped", len(clean) - len(ded), ")")
    clean = ded

    json.dump(clean, open(os.path.join(OUT, "wave_20261116_clean.json"), "w", encoding='utf-8'), ensure_ascii=False)
    json.dump(pending, open(os.path.join(OUT, "wave_20261116_pending.json"), "w", encoding='utf-8'), ensure_ascii=False)
    json.dump(excluded, open(os.path.join(OUT, "wave_20261116_excluded.json"), "w", encoding='utf-8'), ensure_ascii=False)
    json.dump({"stats": dict(stats), "excl_by_reason": dict(excl_counts),
               "clean": len(clean), "pending": len(pending), "excluded": len(excluded)},
              open(os.path.join(OUT, "phase4_stats.json"), "w", encoding='utf-8'), ensure_ascii=False)

    # ---- spot check: >=30 random clean codes + controls ----
    random.seed(20261116)
    sample = random.sample(clean, min(30, len(clean)))
    codes = [c["invite"].split("/")[-1] for c in sample]
    print("spot-checking", len(codes), "clean codes + controls ...", flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(fetch_title, codes))
    live_n = sum(1 for s, _ in results if s == "live")
    print(f"spot-check clean: {live_n}/{len(codes)} live")
    bad = [(c, s) for c, (s, t) in zip(codes, results) if s != "live"]
    print("spot-check non-live:", bad)
    ctrl_live = fetch_title("KrDwdK8EIkB6vgauHg5M7N")
    ctrl_fab = fetch_title("ZzZzZzZzZzZzZzZzZzZzZzZz")
    print("control live:", ctrl_live, "| control fabricated:", ctrl_fab)
    json.dump({"sample_codes": codes, "live": live_n, "total": len(codes),
               "non_live": bad, "control_live": ctrl_live, "control_fab": ctrl_fab},
              open(os.path.join(OUT, "spotcheck.json"), "w", encoding='utf-8'), ensure_ascii=False)
    print("PHASE 4 DONE")

def finish_record(rec, title):
    name = rec["name"] or title
    desc = (rec.get("description") or "").strip()
    if not desc:
        desc = f"Join {name}, a WhatsApp group listed under {rec['category']}."
    return {"name": name, "category": rec["category"], "description": desc,
            "invite": rec["invite"], "country": rec.get("country", ""),
            "image": "", "slug": ""}

if __name__ == "__main__":
    main()
