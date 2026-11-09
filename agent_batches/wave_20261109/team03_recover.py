#!/usr/bin/env python3
"""Recover GCC go.php groupe codes, saving after each id."""
import json, re, subprocess, time, sys
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def run(cmd, timeout=50):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout.decode("utf-8", errors="replace")
    except Exception:
        return -1, ""

def fetch(url, timeout=30):
    rc, out = run(["curl", "-s", "-A", UA, "--max-time", str(timeout), "-L", url], timeout + 10)
    return out if rc == 0 and out else None

raw = json.load(open(f"{WAVE}/team03-raw.json"))
by_url = {r["listing_url"]: r for r in raw}
ids = ['266', '368', '371', '377', '379', '381', '387', '407', '413']
for n in ids:
    cj = f"/tmp/t03_cj_{n}.txt"
    try:
        run(["curl", "-s", "-A", UA, "--max-time", "25", "-c", cj, "-b", cj,
             f"https://groupchatconnect.info/go.php?id={n}", "-o", "/dev/null"], 35)
        run(["curl", "-s", "-A", UA, "--max-time", "25", "-c", cj, "-b", cj,
             "-e", f"https://groupchatconnect.info/go.php?id={n}",
             f"https://groupchatconnect.info/go?id={n}", "-o", "/dev/null"], 35)
        rc, out = run(["curl", "-s", "-A", UA, "--max-time", "25", "-L", "-c", cj, "-b", cj,
                       "-e", f"https://groupchatconnect.info/go?id={n}",
                       f"https://groupchatconnect.info/join.php?id={n}",
                       "-o", "/dev/null", "-w", "%{url_effective}"], 40)
        final = out.strip()
        m = re.search(r'groupsor\.link/group/join/([A-Za-z0-9]+)', final)
        if not m:
            print("FAIL", n, "final:", final[:120], flush=True)
            continue
        token = m.group(1)
        rules = fetch(f"https://groupsor.link/group/rules/{token}/")
        cm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', rules or "")
        url = f"https://groupchatconnect.info/groupe/{n}"
        r = by_url.get(url)
        if cm and r is not None:
            r["code"] = cm.group(1)
            r.pop("error", None)
            r["recovered_via"] = "go.php->join.php->groupsor"
            print("RECOVERED", n, cm.group(1), flush=True)
        else:
            print("FAIL", n, "token", token, "code:", bool(cm), flush=True)
    except Exception as e:
        print("ERR", n, e, flush=True)
    json.dump(raw, open(f"{WAVE}/team03-raw.json", "w"), ensure_ascii=False, indent=1)
    time.sleep(0.5)
print("DONE", flush=True)
