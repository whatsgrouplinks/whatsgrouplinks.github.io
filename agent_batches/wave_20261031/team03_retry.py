#!/usr/bin/env python3
"""team03 retry pass: re-verify all codes marked 'dead' in pass 1 (coordinator advisory).
Elapsed time since pass-1 verdicts already far exceeds the 30-60s pause."""
import json, re, html, time, subprocess, os

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
        return ("transport", None) if not out.strip() else ("dead", None)
    title = html.unescape(m.group(1)).strip()
    return ("live", title) if title else ("dead", None)

def main():
    done = json.load(open(PROG))
    retry_codes = [c for c, (s, t) in done.items() if s == "dead"]
    # also retry old transports once
    retry_codes += [c for c, (s, t) in done.items() if s == "transport"]
    print(f"retrying {len(retry_codes)} codes", flush=True)
    revived, still_dead, transp = 0, 0, 0
    try:
        for idx, code in enumerate(retry_codes):
            st, title = get_title(code)
            if st == "live":
                done[code] = ["live", title]
                revived += 1
                print(f"[{idx+1}] REVIVED {code} :: {title[:60]}", flush=True)
            elif st == "transport":
                transp += 1
            else:
                still_dead += 1
            if (idx + 1) % 20 == 0:
                json.dump(done, open(PROG, "w"))
                print(f"[{idx+1}/{len(retry_codes)}] revived={revived} dead={still_dead} transport={transp}", flush=True)
            time.sleep(0.8)
    finally:
        json.dump(done, open(PROG, "w"))
        print(f"DONE revived={revived} still_dead={still_dead} transport={transp}", flush=True)

if __name__ == "__main__":
    main()
