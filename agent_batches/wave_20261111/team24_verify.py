"""Verify fresh codes from team24_fresh.json (slow sequential, 4s spacing).
Writes team24_verify_fresh.json checkpoint after each code."""
import json, subprocess, re, time, os, sys

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    last_http = "000"
    for attempt in range(3):
        try:
            r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "15", "-w", "\n%{http_code}", url],
                               capture_output=True, text=True, timeout=20)
            body = r.stdout
            m = re.search(r'\n(\d{3})\s*$', body)
            http = m.group(1) if m else "000"
            last_http = http
            html = body[:m.start()] if m else body
            t = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
            if not t:
                t = re.search(r'<meta\s+content="([^"]*)"\s+property="og:title"', html)
            title = t.group(1).strip() if t else ""
            if http == "200" and title:
                return ("live", title, http, "")
            if http in ("200", "000"):
                time.sleep(4)
                continue
            return ("dead", title, http, f"http {http}")
        except Exception:
            time.sleep(4)
            continue
    if last_http == "200":
        return ("dead", "", "200", "empty og:title after retries")
    return ("transport", "", "000", "no http status after 3 attempts")

infile = sys.argv[1] if len(sys.argv) > 1 else "team24_fresh.json"
outfile = sys.argv[2] if len(sys.argv) > 2 else "team24_verify_fresh.json"
cands = json.load(open(W + infile))
out = json.load(open(W + outfile)) if os.path.exists(W + outfile) else {}
for code, v in cands.items():
    if code in out and out[code]["status"] in ("live", "dead"):
        print(code, "skip already", out[code]["status"], flush=True)
        continue
    st, title, http, err = check(code)
    out[code] = {"status": st, "og_title": title, "http": http, "error": err,
                 "name": v.get("name", ""), "page": v.get("page", "")}
    json.dump(out, open(W + outfile, "w"), indent=1, ensure_ascii=False)
    print(code, st, repr(title), http, err, flush=True)
    time.sleep(4)
live = sum(1 for v in out.values() if v["status"] == "live")
dead = sum(1 for v in out.values() if v["status"] == "dead")
tr = sum(1 for v in out.values() if v["status"] == "transport")
print(f"VERIFY DONE total={len(out)} LIVE={live} DEAD={dead} TRANSPORT={tr}")
