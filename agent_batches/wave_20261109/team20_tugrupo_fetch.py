#!/usr/bin/env python3
"""Team 20 wave 20261109 - tugrupo.online detail pages: extract invite + title + desc."""
import json, os, re, subprocess, time, html
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team20_tugrupo_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

urls = json.load(open(os.path.join(WAVE, "team20_tugrupo_detail_urls.json")))
# keep only true group detail pages
bad_suffix = ("/whatsapp", "/chat", "/mundial", "/amor", "/anime", "/diversion",
              "/juegos", "/memes", "/musica", "/peliculas", "/rol", "/stickers", "/destacados")
detail = []
for u in urls:
    if "/page/" in u or "/e/" in u or "/mundial/" in u:
        continue
    if any(u.rstrip("/").endswith(s) for s in bad_suffix):
        continue
    detail.append(u)
print("detail pages:", len(detail))

# reuse already-fetched files
prefetched = {
    "https://tugrupo.online/whatsapp/chat/cristianos-unidos":
        os.path.join(WAVE, "team20_tugrupo_detail.html"),
    "https://tugrupo.online/whatsapp/diversion/venezolanos-en-brasil":
        os.path.join(RAW, "cat_whatsapp_diversion_venezolanos-en-brasil_.html"),
}

def fetch(u):
    slug = re.sub(r"[^A-Za-z0-9]+", "_", u.split("/whatsapp/")[1])[:80]
    out = os.path.join(RAW, f"detail_{slug}.html")
    if u in prefetched:
        return open(prefetched[u], encoding="utf-8", errors="ignore").read()
    if os.path.exists(out) and os.path.getsize(out) > 500:
        return open(out, encoding="utf-8", errors="ignore").read()
    subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA, u, "-o", out],
                   capture_output=True, text=True, timeout=35)
    time.sleep(0.7)
    try:
        return open(out, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""

def clean(t):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or ""))).strip()

results = []
for u in sorted(detail):
    s = fetch(u)
    if not s or len(s) < 500 or "One moment, please" in s[:2000]:
        results.append({"url": u, "status": "fetch-fail/challenge", "bytes": len(s)})
        print("FAIL", u, len(s), flush=True); continue
    title = re.search(r"<title>([^<]*)</title>", s)
    title = clean(title.group(1)) if title else ""
    ogd = re.search(r'<meta property="og:description" content="([^"]*)"', s)
    md = re.search(r'<meta name="description" content="([^"]*)"', s, re.S)
    desc = clean(ogd.group(1)) if ogd else (clean(md.group(1)) if md else "")
    codes = sorted(set(re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})", s)))
    codes = [c.split("?")[0].split("#")[0].rstrip("/") for c in codes]
    fresh = [c for c in codes if c not in existing]
    results.append({"url": u, "status": "ok", "bytes": len(s), "title": title,
                    "desc": desc[:500], "codes": codes, "fresh_codes": fresh})
    print("OK", title[:60], "codes=", codes, "fresh=", fresh, flush=True)

json.dump(results, open(os.path.join(WAVE, "team20_tugrupo_detail.json"), "w"), indent=1, ensure_ascii=False)
print("TOTAL fresh:", sum(len(r.get("fresh_codes", [])) for r in results))
