#!/usr/bin/env python3
"""TEAM30 verify: controls first, then 95 fresh codes, 4 workers, checkpoint JSONL."""
import json, re, time, html, os, threading
import requests
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
SCRATCH = os.path.join(WAVE, "team30_scratch")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
OG_TITLE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_DESC = re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)

DROPS = {
 "CfVetjrgASdJ6HcPLfDUQF": "out of slice: USA (already dropped by team25 wave 20261111; reappeared via whtsgrouplink homepage)",
 "DfG80V91ePEG2LzaLonTHh": "explicit adult group ('Nadeem's adult group')",
 "Cny3X90YPUm47Kx7ieeMD3": "PAK Sim Database — personal-data (SIM) selling / PII trafficking",
 "IJvE84zzn3NGZrGnUQPp7U": "EARN CRYPTO — crypto-earning/airdrop promo (scam screen)",
 "FqH70EzqFNkKgbAfh3hgr6": "Econex online earning — Econex MLM/pyramid earning scheme (scam screen)",
}

def check(session, code, timeout=90):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = session.get(url, headers=UA, timeout=timeout)
        t = OG_TITLE.search(r.text)
        d = OG_DESC.search(r.text)
        title = html.unescape(t.group(1)).strip() if t else ""
        desc = html.unescape(d.group(1)).strip() if d else ""
        return {"code": code, "status": r.status_code, "title": title, "desc": desc, "live": bool(title)}
    except Exception as e:
        return {"code": code, "status": "ERR", "title": "", "desc": "", "live": False, "error": f"{type(e).__name__}: {e}"}

def main():
    fresh = json.load(open(os.path.join(SCRATCH, "fresh_all.json")))
    pool = [f for f in fresh if f["code"] not in DROPS]
    print("pool:", len(pool), "dropped:", len(DROPS), flush=True)
    json.dump([{"code": k, "reason": v} for k, v in DROPS.items()],
              open(os.path.join(SCRATCH, "prescreen_dropped.json"), "w"), indent=1)

    ckpt = os.path.join(SCRATCH, "verify_results.jsonl")
    done = {}
    if os.path.exists(ckpt):
        for line in open(ckpt):
            try:
                d = json.loads(line)
                done[d["code"]] = d
            except Exception:
                pass
    print("resuming with", len(done), "already checked", flush=True)
    lock = threading.Lock()

    def worker(code):
        if code in done:
            return done[code]
        s = requests.Session()
        res = check(s, code)
        # retry once on empty (not live) or transport error, after a pause
        if (not res["live"]) and res.get("status") != "ERR":
            time.sleep(20)
            res2 = check(s, code)
            if res2["live"]:
                res = res2
            else:
                res["retried_empty"] = True
        elif res.get("status") == "ERR":
            time.sleep(20)
            res2 = check(s, code)
            if res2["live"] or res2.get("status") != "ERR":
                res = res2
            else:
                res["retried_err"] = True
        with lock:
            done[code] = res
            with open(ckpt, "a") as f:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")
            print(res["code"], res.get("status"), "LIVE" if res["live"] else "dead/err", (res.get("title") or "")[:60], flush=True)
        return res

    # NOTE: og:description is NOT a liveness fallback — dead control returns
    # generic desc "WhatsApp Group Invite" with empty og:title. LIVE = non-empty og:title only (team25 precedent).
    s = requests.Session()
    live_ctrl = check(s, "00CHZw0BFnP6ZLQVROVo0Y")
    print("CONTROL live 00CHZw0BFnP6ZLQVROVo0Y:", live_ctrl, flush=True)
    dead_ctrl = check(s, "ZZZZZZZZZZZZZZZZZZZZZZ")
    print("CONTROL fabricated ZZZZ...:", dead_ctrl, flush=True)
    assert live_ctrl["live"], "LIVE CONTROL FAILED — abort"
    assert not dead_ctrl["live"], "DEAD CONTROL FAILED — abort"
    with open(os.path.join(SCRATCH, "controls.json"), "w") as f:
        json.dump({"live_control": live_ctrl, "dead_control": dead_ctrl}, f, indent=1)

    codes = [f["code"] for f in pool]
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(worker, codes))
    live = [d for d in done.values() if d["live"]]
    dead = [d for d in done.values() if not d["live"] and d.get("status") != "ERR"]
    pend = [d for d in done.values() if d.get("status") == "ERR"]
    print(f"RESULT live={len(live)} dead={len(dead)} pending(err)={len(pend)} total={len(done)}")
    json.dump({"live": live, "dead": dead, "pending": pend}, open(os.path.join(SCRATCH, "verify_summary.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
