import json, subprocess, re, time, sys
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
pend = json.load(open(W + "team24-pending-in.json"))

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
        except Exception as e:
            time.sleep(4)
            continue
    if last_http == "200":
        return ("dead", "", "200", "empty og:title after retries")
    return ("transport", "", "000", "no http status after 3 attempts")

out = {}
for p in pend:
    code = p["invite"].rstrip("/").split("/")[-1]
    st, title, http, err = check(code)
    out[code] = {"status": st, "og_title": title, "http": http, "error": err, "name": p["name"]}
    json.dump(out, open(W + "team24_pending_recheck.json", "w"), indent=1, ensure_ascii=False)
    print(code, st, repr(title), http, err, flush=True)
    time.sleep(4)
live = sum(1 for v in out.values() if v["status"] == "live")
dead = sum(1 for v in out.values() if v["status"] == "dead")
tr = sum(1 for v in out.values() if v["status"] == "transport")
print(f"PENDING RECHECK DONE LIVE={live} DEAD={dead} TRANSPORT={tr}")
