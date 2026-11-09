#!/usr/bin/env python3
"""Team 03 repair pass: recover codes for GCC /go.php?id=N groupe pages,
retry failed GCC /channel/ fetches, inspect no-token channel pages."""
import json, re, subprocess, sys, time, html
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def run(cmd, timeout=45):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        return -1, ""

def fetch(url, timeout=30):
    rc, out = run(["curl", "-s", "-A", UA, "--max-time", str(timeout), "-L", url], timeout + 10)
    return out if rc == 0 and out else None

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(s or "")).strip()

raw = json.load(open(f"{WAVE}/team03-raw.json"))
by_url = {r["listing_url"]: r for r in raw}

# --- 1. go.php groupe ids ---
gophp_ids = []
for r in raw:
    if r.get("source") == "groupchatconnect.info" and r.get("error") == "no /go/ token found" and "/groupe/" in r["listing_url"]:
        gophp_ids.append(r["listing_url"].rstrip('/').split('/')[-1])
print("go.php groupe ids:", gophp_ids)

def recover_gophp(n):
    # join.php?id=N -> 301 to groupsor /group/join/<token>
    rc, out = run(["curl", "-s", "-A", UA, "--max-time", "30",
                   "-o", "/dev/null", "-w", "%{url_effective}",
                   f"https://groupchatconnect.info/join.php?id={n}"], 45)
    final = out.strip()
    m = re.search(r'groupsor\.link/group/join/([A-Za-z0-9]+)', final)
    if not m:
        return n, None, f"join.php final url unexpected: {final[:120]}"
    token = m.group(1)
    rules = fetch(f"https://groupsor.link/group/rules/{token}/")
    if not rules:
        return n, token, "groupsor rules fetch failed"
    cm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', rules)
    if cm:
        return n, cm.group(1), None
    return n, token, "no code on groupsor rules page"

with ThreadPoolExecutor(max_workers=3) as ex:
    for n, code, err in ex.map(recover_gophp, gophp_ids):
        url = f"https://groupchatconnect.info/groupe/{n}"
        r = by_url.get(url)
        if r is None:
            continue
        if code and not err:
            r["code"] = code
            r.pop("error", None)
            r["recovered_via"] = "go.php->join.php->groupsor"
            print("RECOVERED", n, code)
        else:
            r["error"] = f"go.php recovery failed: {err}"
            print("FAIL", n, err)
        time.sleep(0.2)

# --- 2. retry failed channel fetches + inspect no-token channels ---
chan_urls = [r["listing_url"] for r in raw
             if r.get("source") == "groupchatconnect.info"
             and (r.get("error") == "detail fetch failed" or r.get("error") == "no /go/ token found")
             and "/channel/" in r["listing_url"]]
print("channel urls to recheck:", len(chan_urls))

def check_channel(url):
    h = fetch(url)
    if not h:
        return url, None, "fetch failed again"
    m = re.search(r'<title>(.*?)</title>', h, re.S)
    title = clean(m.group(1)) if m else ""
    is_channel = "قناة" in title or "قناة" in h[:5000] or "/channels" in h
    join = re.search(r'href="(/go[^"]*|/go\.php[^"]*)"', h)
    gophp = re.search(r'href="(/go\.php\?id=\d+)"', h)
    return url, {"title": title, "is_channel": is_channel,
                 "has_go": bool(join), "go_href": gophp.group(1) if gophp else None}, None

with ThreadPoolExecutor(max_workers=3) as ex:
    for url, info, err in ex.map(check_channel, chan_urls):
        r = by_url.get(url)
        if err:
            print("CHAN FAIL", url, err)
            continue
        print("CHAN", url.split('/')[-1], "| channel?", info["is_channel"], "| go?", info["go_href"], "|", info["title"][:80])
        if r is not None:
            r["channel_check"] = info
            if info["is_channel"] and not info["go_href"]:
                r["error"] = "channel-only page (no group invite)"
            elif info["go_href"]:
                r.pop("error", None)
                r["go_href"] = info["go_href"]

json.dump(raw, open(f"{WAVE}/team03-raw.json", "w"), ensure_ascii=False, indent=1)
print("raw updated")
