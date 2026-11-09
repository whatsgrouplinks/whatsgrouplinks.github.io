#!/usr/bin/env python3
"""Team 20 wave 20261109 - igrupos detail sweep, gids 523700..523779 (below 5238xx)."""
import json, os, re, subprocess, time, html
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team20_igrupos_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

def fetch(gid):
    out = os.path.join(RAW, f"{gid}.html")
    if os.path.exists(out) and os.path.getsize(out) > 500:
        return open(out, encoding="utf-8", errors="ignore").read()
    r = subprocess.run(["curl", "-sL", "--max-time", "20", "-A", UA,
                        f"https://www.igrupos.com/grupo/{gid}", "-o", out],
                       capture_output=True, text=True, timeout=30)
    time.sleep(0.6)
    try:
        return open(out, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""

results = []
for gid in range(523700, 523780):
    s = fetch(gid)
    if not s or len(s) < 500:
        results.append({"gid": gid, "status": "fetch-fail", "bytes": len(s)})
        print(gid, "FETCH-FAIL", len(s), flush=True); continue
    title = re.search(r"<title>([^<]*)</title>", s)
    title = html.unescape(title.group(1)).strip() if title else ""
    desc = re.search(r'<meta name="description" content="([^"]*)"', s, re.S)
    desc = html.unescape(desc.group(1)).strip() if desc else ""
    wa = re.findall(r"window\.open\('(https://chat\.whatsapp\.com/[^']+)'", s)
    tg = re.findall(r"window\.open\('(https://telegram\.me/[^']+)'", s)
    wa2 = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})", s)
    is_wa = "grupos de whatsapp" in s.lower()
    flags = re.findall(r"banderas64/([A-Z]{2})\.png", s)
    codes = []
    for link in wa:
        m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]+)", link)
        if m: codes.append(m.group(1).split("?")[0].split("#")[0].rstrip("/"))
    fresh = [c for c in codes if c not in existing]
    results.append({"gid": gid, "status": "ok", "bytes": len(s), "title": title,
                    "desc": desc[:400], "is_whatsapp": is_wa, "flags": flags[:4],
                    "wa_links": wa, "tg_links": tg, "codes": codes, "fresh_codes": fresh,
                    "wa_links_any": list(set(wa2))[:3]})
    print(gid, "wa" if is_wa else "tg?", "title=", title[:40], "codes=", codes, "fresh=", fresh, "flags=", flags[:2], flush=True)

json.dump(results, open(os.path.join(WAVE, "team20_igrupos_sweep.json"), "w"), indent=1, ensure_ascii=False)
fresh_all = [c for r in results for c in r.get("fresh_codes", [])]
print("TOTAL fresh codes:", len(fresh_all), fresh_all)
print("TOTAL ok pages:", sum(1 for r in results if r["status"] == "ok"))
