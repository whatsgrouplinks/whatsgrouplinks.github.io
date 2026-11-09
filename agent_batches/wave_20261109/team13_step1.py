#!/usr/bin/env python3
"""Team 13 wave 20261109 - grupbul.com categories.
Step 1: fetch category listing pages -> group ids.
Step 2: fetch each group page -> /redirect/<gid>/<n> -> refresh header -> chat code.
Step 3: dedupe vs existing, screen, slow-verify via curl, write outputs.
"""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team13_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

CATS = [
    ("Game", "https://grupbul.com/en/category/whatsapp/5/game"),
    ("News", "https://grupbul.com/en/category/whatsapp/8/news"),
    ("Religion", "https://grupbul.com/en/category/whatsapp/52/religion"),
    ("Technology", "https://grupbul.com/en/category/whatsapp/38/technology"),
    ("Trade", "https://grupbul.com/en/category/whatsapp/29/trade"),
    ("Travel", "https://grupbul.com/en/category/whatsapp/54/travel"),
    ("Food", "https://grupbul.com/en/category/whatsapp/53/food"),
    ("Student", "https://grupbul.com/en/category/whatsapp/35/student"),
    ("Series/Movie", "https://grupbul.com/en/category/whatsapp/47/series-movie"),
    ("Job Postings", "https://grupbul.com/en/category/whatsapp/9/job-postings"),
    ("Music", "https://grupbul.com/en/category/whatsapp/34/music"),
    ("Chat/Friendship", "https://grupbul.com/en/category/whatsapp/15/chat-friendship"),
]
EXTRA = [
    ("All-WhatsApp", "https://grupbul.com/en/whatsapp-groups"),
    ("Chat/Friendship-page", "https://grupbul.com/en/whatsapp-chat-friendship-groups"),
    ("Job-Postings-page", "https://grupbul.com/en/whatsapp-job-posting-groups"),
]

existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
print("existing codes:", len(existing), flush=True)

def curl_get(url, outpath, max_time=30):
    if os.path.exists(outpath) and os.path.getsize(outpath) > 500:
        return open(outpath, encoding="utf-8", errors="ignore").read()
    r = subprocess.run(["curl", "-sL", "--max-time", str(max_time), "-A", UA,
                        "-o", outpath, "-w", "%{http_code}", url],
                       capture_output=True, text=True, timeout=max_time + 15)
    try:
        return open(outpath, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""

def clean_text(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

# ---- Step 1: category pages ----
groups = {}  # gid -> {"name":, "cat":, "from":, "desc":}
coverage = []
def fetch_cat(item):
    cat, url = item
    fn = os.path.join(RAW, "cat-" + re.sub(r"[^a-z0-9]+", "-", cat.lower()) + ".html")
    html = curl_get(url, fn)
    ids = sorted(set(re.findall(r"/group/(\d+)", html)))
    # listing entries: name + desc near each /group/ link
    for gid in ids:
        m = re.search(r"/group/" + gid + r"[^>]*>(.*?)Join", html, re.S)
        name, desc = "", ""
        if m:
            seg = clean_text(m.group(1))
            # seg looks like "NAME Game Welcome to ... description..."
            name = seg.split("  ")[0][:120]
            desc = seg[len(name):].strip()[:400]
        groups.setdefault(gid, {"gid": gid, "cat": cat, "from": url, "list_name": name, "list_desc": desc})
    time.sleep(0.5)
    print(f"CAT {cat}: {len(ids)} groups, {len(html)} bytes", flush=True)
    return {"category": cat, "url": url, "bytes": len(html), "group_ids": ids}

with ThreadPoolExecutor(max_workers=3) as ex:
    coverage = list(ex.map(fetch_cat, CATS))
for item in EXTRA:
    cat, url = item
    fn = os.path.join(RAW, "extra-" + re.sub(r"[^a-z0-9]+", "-", cat.lower()) + ".html")
    html = curl_get(url, fn)
    ids = sorted(set(re.findall(r"/group/(\d+)", html)))
    for gid in ids:
        groups.setdefault(gid, {"gid": gid, "cat": "Unknown", "from": url, "list_name": "", "list_desc": ""})
    coverage.append({"category": cat, "url": url, "bytes": len(html), "group_ids": ids})
    print(f"EXTRA {cat}: {len(ids)} groups", flush=True)
    time.sleep(0.5)

print("TOTAL unique group ids from listings:", len(groups), flush=True)
json.dump({"coverage": coverage, "groups": groups},
          open(os.path.join(WAVE, "team13_step1.json"), "w"), indent=1)
print("step1 done", flush=True)
