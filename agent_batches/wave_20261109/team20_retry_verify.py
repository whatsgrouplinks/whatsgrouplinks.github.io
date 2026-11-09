#!/usr/bin/env python3
"""Team 20 - retry failed tugrupo detail pages once, then slow-verify all fresh codes."""
import json, os, re, subprocess, time, html
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team20_tugrupo_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

# --- 1. retry failed tugrupo detail pages ---
det = json.load(open(os.path.join(WAVE, "team20_tugrupo_detail.json")))
failed = [r for r in det if r["status"] != "ok"]
print("retrying", len(failed), "failed tugrupo pages")
for r in failed:
    u = r["url"]
    slug = re.sub(r"[^A-Za-z0-9]+", "_", u.split("/whatsapp/")[1])[:80]
    out = os.path.join(RAW, f"detail_{slug}.html")
    subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, u, "-o", out],
                   capture_output=True, text=True, timeout=40)
    time.sleep(1.0)
    try:
        s = open(out, encoding="utf-8", errors="ignore").read()
    except Exception:
        s = ""
    if not s or len(s) < 500 or "One moment, please" in s[:2000]:
        r["status"] = "fetch-fail-retry"; r["bytes"] = len(s)
        print("RETRY-FAIL", u, len(s), flush=True); continue
    title = re.search(r"<title>([^<]*)</title>", s)
    title = html.unescape(re.sub(r"\s+", " ", title.group(1))).strip() if title else ""
    ogd = re.search(r'<meta property="og:description" content="([^"]*)"', s)
    md = re.search(r'<meta name="description" content="([^"]*)"', s, re.S)
    desc = html.unescape(ogd.group(1)).strip() if ogd else (html.unescape(md.group(1)).strip() if md else "")
    codes = sorted(set(re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})", s)))
    codes = [c.split("?")[0].split("#")[0].rstrip("/") for c in codes]
    r.update({"status": "ok-retry", "bytes": len(s), "title": title,
              "desc": desc[:500], "codes": codes,
              "fresh_codes": [c for c in codes if c not in existing]})
    print("RETRY-OK", title[:60], "codes=", codes, "fresh=", r["fresh_codes"], flush=True)
json.dump(det, open(os.path.join(WAVE, "team20_tugrupo_detail.json"), "w"), indent=1, ensure_ascii=False)

# --- 2. collect all fresh codes ---
igr = json.load(open(os.path.join(WAVE, "team20_igrupos_sweep.json")))
cands = {}  # code -> record
for r in igr:
    for c in r.get("fresh_codes", []):
        cands[c] = {"code": c, "source": "igrupos", "gid": r["gid"],
                    "page_title": r.get("title", ""), "page_desc": r.get("desc", ""),
                    "flags": r.get("flags", [])}
for r in det:
    for c in r.get("fresh_codes", []):
        cands[c] = {"code": c, "source": "tugrupo", "url": r["url"],
                    "page_title": r.get("title", ""), "page_desc": r.get("desc", "")}
# hard screen BEFORE verify: explicit sexual title
drop = []
for c, rec in list(cands.items()):
    t = (rec.get("page_title", "") + " " + rec.get("page_desc", "")).lower()
    if "mi pito" in t or "pito en" in t:
        drop.append(c); del cands[c]
print("pre-screen dropped:", drop)
print("codes to verify:", len(cands))
json.dump(cands, open(os.path.join(WAVE, "team20_to_verify.json"), "w"), indent=1, ensure_ascii=False)

# --- 3. slow verify each code via curl (never python requests) ---
def og_check(code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in (1, 2, 3):
        out = os.path.join(WAVE, f"team20_verify_{code}.html")
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "30", "-A", UA,
                            "-o", out, "-w", "%{http_code}", url],
                           capture_output=True, text=True, timeout=40)
        http = (r.stdout or "").strip()
        try:
            s = open(out, encoding="utf-8", errors="ignore").read()
        except Exception:
            s = ""
        m = re.search(r'<meta property="og:title" content="([^"]*)"', s)
        title = html.unescape(m.group(1)).strip() if m else ""
        m2 = re.search(r'<meta property="og:description" content="([^"]*)"', s)
        desc = html.unescape(m2.group(1)).strip() if m2 else ""
        if http == "200" and title:
            return {"http": http, "og_title": title, "og_desc": desc, "attempts": attempt, "verdict": "LIVE"}
        time.sleep(3)
    return {"http": http, "og_title": title, "og_desc": desc, "attempts": 3,
            "verdict": "DEAD" if http != "200" else "AMBIGUOUS-EMPTY-TITLE"}

results = {}
for code, rec in sorted(cands.items()):
    v = og_check(code)
    rec.update(v)
    results[code] = rec
    print(code, v["verdict"], "http=", v["http"], "og=", repr(v["og_title"][:60]), "src=", rec["source"], flush=True)
    time.sleep(1.0)
json.dump(results, open(os.path.join(WAVE, "team20_verified.json"), "w"), indent=1, ensure_ascii=False)
print("LIVE:", sum(1 for r in results.values() if r["verdict"] == "LIVE"))
print("DEAD:", sum(1 for r in results.values() if r["verdict"] == "DEAD"))
print("AMBIG:", sum(1 for r in results.values() if r["verdict"].startswith("AMBIG")))
