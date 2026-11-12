#!/usr/bin/env python3
"""TEAM32 step 5: fix virenial names (concat split anchors); resolve shopee bit.ly;
attempt groupwa wagd_more ajax; inspect joinnchat mechanism + helloworldawaits."""
import json, re, html, subprocess, time, urllib.parse

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
RAW = WAVE + "team32_raw/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
log = open(WAVE + "team32_step5.log", "a")
def say(s):
    print(s, flush=True); log.write(s + "\n"); log.flush()

# --- 1. virenial names: concat all anchor texts per code in order
v = open(RAW + "virenial_yt.html", encoding="utf-8", errors="ignore").read()
names = {}
for m in re.finditer(r"handler\?url=https%3A%2F%2Fchat\.whatsapp\.com%2F([A-Za-z0-9_-]{15,30})[^>]*>(.*?)</a>", v, re.S):
    code, txt = m.group(1), html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
    names.setdefault(code, "")
    names[code] += txt
# clean: collapse whitespace
names = {c: re.sub(r"\s+", " ", t).strip() for c, t in names.items()}
fresh = json.load(open(WAVE + "team32_pool_fresh.json"))
nfix = 0
for p in fresh:
    if p["source"] == "virenial_yt" and p["code"] in names and names[p["code"]]:
        if p["name"] != names[p["code"]]:
            nfix += 1
        p["name"] = names[p["code"]]
json.dump(fresh, open(WAVE + "team32_pool_fresh.json", "w"), indent=1, ensure_ascii=False)
say(f"virenial names fixed/concatenated: {nfix} changed; sample:")
for p in fresh[:5]:
    if p["source"] == "virenial_yt":
        say(f"  {p['code']} | {p['name'][:80]}")

# --- 2. shopee bit.ly resolution
rows = json.load(open(WAVE + "team32_shopee_rows.json"))
resolved = []
for r in rows:
    url = r["bitly"]
    final, err = "", ""
    for attempt in range(2):
        try:
            pr = subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-A", UA,
                                 "-o", "/dev/null", "-w", "%{url_effective} %{http_code}", url],
                                capture_output=True, text=True, timeout=75)
            out = pr.stdout.strip()
            final = out.rsplit(" ", 1)[0] if out else ""
            err = f"rc={pr.returncode} {pr.stderr.strip()[:100]}"
            if final and "bit.ly" not in final:
                break
        except subprocess.TimeoutExpired:
            err = "timeout"
        time.sleep(5)
    m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", final)
    code = m.group(1) if m else ""
    say(f"shopee {url} -> {final[:90]} code={code or '-'} {err}")
    resolved.append({**r, "final_url": final, "code": code, "err": err})
    json.dump(resolved, open(WAVE + "team32_shopee_resolved.json", "w"), indent=1, ensure_ascii=False)
    time.sleep(3)
say(f"shopee resolved with code: {sum(1 for r in resolved if r['code'])} / {len(resolved)}")

# --- 3. groupwa wagd_more ajax attempt
# Inspect team27 extract script for ajax hints first via the saved gw html
gw = open(RAW + "groupwa_jobs.html", encoding="utf-8", errors="ignore").read()
for pat in ["wag_more", "wag_more", "admin-ajax", "load-more", "data-page", "page="]:
    idxs = [m.start() for m in re.finditer(re.escape(pat), gw)][:3]
    if idxs:
        say(f"groupwa ajax hint '{pat}': {[gw[max(0,i-80):i+120].replace(chr(10),' ') for i in idxs][:2]}")
import requests
sess = requests.Session(); sess.headers.update({"User-Agent": UA})
for endpoint in ["https://groupwa.link/wp-admin/admin-ajax.php"]:
    for payload in [{"action": "wag_more", "page": 2, "cat": "jobs"},
                    {"action": "wag_more", "page": 2, "category": "jobs"},
                    {"action": "load_more", "page": 2}]:
        try:
            r = sess.post(endpoint, data=payload, timeout=60)
            say(f"ajax POST {payload}: status={r.status_code} len={len(r.text)} snippet={r.text[:200]!r}")
            open(RAW + "groupwa_ajax_try.html", "w").write(r.text)
            break
        except Exception as e:
            say(f"ajax POST {payload} FAIL: {type(e).__name__}: {e}")
log.close()
