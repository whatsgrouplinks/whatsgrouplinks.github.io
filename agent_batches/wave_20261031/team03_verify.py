#!/usr/bin/env python3
"""team03: verify candidates via WhatsApp invite og:title."""
import json, re, html, time, subprocess, sys, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
PROG = "/tmp/team03_progress.json"

def get_title(code):
    try:
        p = subprocess.run(
            ["curl", "-sL", "--max-time", "25", "-A", UA,
             f"https://chat.whatsapp.com/{code}"],
            capture_output=True, text=True, timeout=35)
        out = p.stdout
    except Exception:
        return ("transport", None)
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', out)
    if not m:
        m = re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", out)
    if not m:
        # empty/blocked response -> transport; a real page always carries og:title tag
        return ("transport", None)
    title = html.unescape(m.group(1)).strip()
    if title:
        return ("live", title)
    return ("dead", None)

def main():
    cands = json.load(open("/tmp/team03_cands.json"))
    done = {}
    if os.path.exists(PROG):
        done = json.load(open(PROG))
    verified, pending, dead = [], [], []
    # restore already processed
    for c in cands:
        code = c["code"]
        if code in done:
            st, t = done[code]
            if st == "live": verified.append((c, t))
            elif st == "pending": pending.append((c, t))
            else: dead.append(code)
    print(f"resuming: {len(verified)} verified, {len(pending)} pending, {len(dead)} dead", flush=True)
    try:
        for idx, c in enumerate(cands):
            code = c["code"]
            if code in done:
                continue
            st, title = get_title(code)
            done[code] = [st, title]
            if st == "live":
                verified.append((c, title))
            elif st == "dead":
                dead.append(code)
            else:
                pending.append((c, "transport failure"))
            if len(done) % 20 == 0:
                json.dump(done, open(PROG, "w"))
                print(f"[{idx+1}/{len(cands)}] verified={len(verified)} pending={len(pending)} dead={len(dead)}", flush=True)
            time.sleep(0.6)
    finally:
        json.dump(done, open(PROG, "w"))
        json.dump({"verified": [(c, t) for c, t in verified],
                   "pending": [{"code": c["code"], "name": c["name"], "note": n, "cand": c} for c, n in pending],
                   "dead_count": len(dead)},
                  open("/tmp/team03_verify_result.json", "w"), ensure_ascii=False)
        print(f"DONE verified={len(verified)} pending={len(pending)} dead={len(dead)}", flush=True)

if __name__ == "__main__":
    main()
