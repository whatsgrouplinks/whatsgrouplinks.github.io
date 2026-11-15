#!/usr/bin/env python3
"""team19 wave 20261114: groupsnest + grouplinksforyou new-post poll."""
import json, re, hashlib, subprocess, sys, time, os, html
from pathlib import Path
import requests

WAVE = Path("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
PREV = Path("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113/team22_scratch")
SCR = WAVE / "team19_scratch"
SCR.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

def og_title(page):
    m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']*)["\']', page, re.I)
    if not m:
        m = re.search(r'<meta\s+content=["\']([^"\']*)["\']\s+property=["\']og:title["\']', page, re.I)
    return html.unescape(m.group(1).strip()) if m else ""

# ---- 1. CONTROLS FIRST (single keep-alive session) ----
s = requests.Session()
s.headers.update(UA)
controls = {}
for code, expect in [("KrDwdK8EIkB6vgauHg5M7N", "JAY - PHP & Python Full Stack Developer"),
                     ("ZzZzZzZzZzZzZzZzZzZzZz", "")]:
    title = None
    for attempt in range(3):
        try:
            r = s.get(f"https://chat.whatsapp.com/{code}", timeout=75)
            (SCR / f"ctrl_{code}.html").write_bytes(r.content)
            title = og_title(r.text)
            break
        except Exception as e:
            title = f"ERROR:{e}"
            time.sleep(5)
    controls[code] = title
    print(f"CONTROL {code}: og:title={title!r} expect={expect!r} -> {'PASS' if title==expect else 'FAIL'}", flush=True)
if controls["KrDwdK8EIkB6vgauHg5M7N"] != "JAY - PHP & Python Full Stack Developer" or controls["ZzZzZzZzZzZzZzZzZzZzZz"] != "":
    print("CONTROLS FAILED - STOPPING", flush=True)
    (WAVE / "team19-controls-failed.json").write_text(json.dumps(controls, indent=1))
    sys.exit(2)
print("CONTROLS PASS", flush=True)

# ---- 2. curl fetch helper (urllib fails on groupsnest per prior runs) ----
def curl_fetch(url, out, tries=3):
    for i in range(tries):
        p = subprocess.run(["curl", "-sS", "-L", "--max-time", "90", "-A", UA["User-Agent"], "-o", str(out), url],
                           capture_output=True, text=True)
        if p.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return True
        time.sleep(5)
    return False

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

results = {"controls": controls}

# groupsnest sitemap
ok = curl_fetch("https://groupsnest.com/sitemap-posts.xml", SCR / "sitemap-posts.xml")
sm = (SCR / "sitemap-posts.xml").read_text(errors="replace")
urls = re.findall(r"<loc>([^<]+)</loc>", sm)
lastmods = re.findall(r"<lastmod>([^<]+)</lastmod>", sm)
prev_sm = (PREV / "sitemap-posts.xml").read_bytes()
results["groupsnest_sitemap"] = {
    "fetched": ok, "sha256": sha(SCR / "sitemap-posts.xml"),
    "prev_sha256": hashlib.sha256(prev_sm).hexdigest(),
    "identical_to_20261113": (SCR / "sitemap-posts.xml").read_bytes() == prev_sm,
    "urls": len(urls), "newest_lastmod": max(lastmods) if lastmods else None,
    "new_urls": sorted(set(urls) - set(re.findall(r"<loc>([^<]+)</loc>", prev_sm.decode(errors="replace")))),
    "dropped_urls": sorted(set(re.findall(r"<loc>([^<]+)</loc>", prev_sm.decode(errors="replace"))) - set(urls)),
}
print("GROUPSNEST SITEMAP:", json.dumps(results["groupsnest_sitemap"], indent=1), flush=True)

# grouplinksforyou feeds + sitemap
for name, url in [("feed.json", "https://www.grouplinksforyou.com/feeds/posts/default?alt=json&max-results=500"),
                  ("feed_p2.json", "https://www.grouplinksforyou.com/feeds/posts/default?alt=json&max-results=500&start-index=34"),
                  ("sitemap-glfy.xml", "https://www.grouplinksforyou.com/sitemap.xml")]:
    ok = curl_fetch(url, SCR / name)
    same = (SCR / name).read_bytes() == (PREV / name).read_bytes() if (PREV / name).exists() else None
    print(f"GLFY {name}: fetched={ok} identical_to_20261113={same} size={(SCR/name).stat().st_size}", flush=True)
    results[f"glfy_{name}"] = {"fetched": ok, "identical_to_20261113": same,
                               "sha256": sha(SCR / name),
                               "prev_sha256": hashlib.sha256((PREV / name).read_bytes()).hexdigest() if (PREV / name).exists() else None}

def feed_entries(path):
    d = json.loads(Path(path).read_text())
    feed = d.get("feed", {})
    entries = feed.get("entry", [])
    out = []
    for e in entries:
        title = e.get("title", {}).get("$t", "")
        upd = e.get("updated", {}).get("$t", "")
        link = ""
        for l in e.get("link", []):
            if l.get("rel") == "alternate":
                link = l.get("href", "")
        out.append({"title": title, "updated": upd, "link": link})
    return feed.get("updated", {}).get("$t"), out

glfy = {}
for name in ["feed.json", "feed_p2.json"]:
    upd, entries = feed_entries(SCR / name)
    glfy[name] = {"feed_updated": upd, "entries": len(entries), "list": entries}
    print(f"GLFY {name}: entries={len(entries)} feed_updated={upd}", flush=True)
prev_e1 = feed_entries(PREV / "feed.json")[1]
prev_e2 = feed_entries(PREV / "feed_p2.json")[1]
all_new = glfy["feed.json"]["list"] + glfy["feed_p2.json"]["list"]
all_prev = prev_e1 + prev_e2
new_posts = [e for e in all_new if (e["title"], e["link"]) not in {(p["title"], p["link"]) for p in all_prev}]
removed = [e for e in all_prev if (e["title"], e["link"]) not in {(p["title"], p["link"]) for p in all_new}]
changed = [e for e in all_new if any(p["title"] == e["title"] and p["updated"] != e["updated"] for p in all_prev)]
results["grouplinksforyou"] = {
    "feed_page1_entries": glfy["feed.json"]["entries"],
    "feed_page2_entries": glfy["feed_p2.json"]["entries"],
    "total_results": len(all_new),
    "feed_updated_field": glfy["feed.json"]["feed_updated"],
    "new_posts_vs_20261113": len(new_posts), "new_posts": new_posts,
    "removed_posts_vs_20261113": len(removed), "removed_posts": removed,
    "changed_posts_vs_20261113": len(changed), "changed_posts": changed,
    "newest_updated": max((e["updated"] for e in all_new), default=None),
    "oldest_updated": min((e["updated"] for e in all_new), default=None),
    "sitemap_identical_to_20261113": results["glfy_sitemap-glfy.xml"]["identical_to_20261113"],
}
print("GLFY SUMMARY:", json.dumps(results["grouplinksforyou"], indent=1)[:2000], flush=True)

# ---- 3. groupsnest collection pages (33) ----
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})")
def codes_of(path):
    return set(CODE_RE.findall(Path(path).read_text(errors="replace")))

per_page, failed = {}, []
all_codes = set()
for u in urls:
    slug = u.rstrip("/").split("/")[-1]
    out = SCR / f"coll_{slug}.html"
    ok = curl_fetch(u, out)
    if not ok:
        failed.append(u)
        continue
    codes = codes_of(out)
    prev = codes_of(PREV / f"coll_{slug}.html") if (PREV / f"coll_{slug}.html").exists() else set()
    per_page[slug] = {"count": len(codes), "prev_count": len(prev),
                      "new": sorted(codes - prev), "gone": sorted(prev - codes)}
    all_codes |= codes
    print(f"COLL {slug}: {len(codes)} (prev {len(prev)}) new={len(codes-prev)} gone={len(prev-codes)}", flush=True)

results["groupsnest_collections"] = {
    "fetched": len(per_page), "failed": failed,
    "extracted_unique_codes": len(all_codes),
    "new_codes": sorted(set().union(*[set(v["new"]) for v in per_page.values()]) if per_page else set()),
    "gone_codes": sorted(set().union(*[set(v["gone"]) for v in per_page.values()]) if per_page else set()),
    "per_page": per_page,
}
print("COLLECTIONS:", json.dumps({k: v for k, v in results["groupsnest_collections"].items() if k != "per_page"}, indent=1), flush=True)

(WAVE / "team19_poll_raw.json").write_text(json.dumps(results, indent=1))
print("RAW SAVED", flush=True)
