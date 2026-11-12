#!/usr/bin/env python3
"""TEAM32 step 3: extract codes+names from virenial, grouplinksforyou feed,
grouplink_intl, techsslash, groupwa pages, shopee bit.ly table; resolve bit.ly."""
import json, re, html, os, subprocess, urllib.parse

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
RAW = WAVE + "team32_raw/"
def load(k): return open(RAW + k + ".html", encoding="utf-8", errors="ignore").read()

pool = {}  # code -> {name, source, raw_name}
def add(code, name, source):
    if not re.fullmatch(r"[A-Za-z0-9_-]{15,30}", code or ""):
        return
    if code not in pool:
        pool[code] = {"code": code, "name": (name or "").strip(), "source": source}
    elif not pool[code]["name"] and name:
        pool[code]["name"] = name.strip()

# --- A. virenial: handler?url=https%3A%2F%2Fchat.whatsapp.com%2FCODE, anchor text = name
v = load("virenial_yt")
for m in re.finditer(r"handler\?url=https%3A%2F%2Fchat\.whatsapp\.com%2F([A-Za-z0-9_-]{15,30})[^>]*>(.*?)</a>", v, re.S):
    nm = re.sub(r"<[^>]+>", "", m.group(2))
    nm = html.unescape(nm).strip()
    add(m.group(1), nm, "virenial_yt")
print("virenial codes:", sum(1 for c in pool.values() if c["source"]=="virenial_yt"))

# --- B. grouplinksforyou feed: JSON with escaped chat.whatsapp.com\/CODE
g = load("grouplinksforyou_feed")
try:
    data = json.loads(g)
    entries = data.get("feed", {}).get("entry", [])
except Exception as e:
    print("feed JSON parse fail:", e); entries = []
print("feed entries:", len(entries))
SE = ["philippin", "indonesia", "malaysia", "thailand", "vietnam", "singapore", "kuala lumpur", "manila", "jakarta", "bangkok", "hanoi", "ho chi minh", "cambodia", "laos", "myanmar", "brunei", "timor", "southeast asia", "south east asia", "sea "]
for e in entries:
    title = e.get("title", {}).get("$t", "")
    content = ""
    for c in e.get("content", {}).values():
        pass
    content = e.get("content", {}).get("$t", "") or ""
    summary = e.get("summary", {}).get("$t", "") or ""
    blob = title + "\n" + content + "\n" + summary
    codes = sorted(set(re.findall(r"chat\.whatsapp\.com(?:\\?/)([A-Za-z0-9_-]{15,30})", blob)))
    if not codes:
        continue
    # name per code: find <a href=...code...>text</a> in content
    for code in codes:
        nm = ""
        mm = re.search(r"chat\.whatsapp\.com(?:\\?/)" + re.escape(code) + r"[^>]*>([^<]{2,80})", blob)
        if mm:
            nm = html.unescape(mm.group(1)).strip()
        add(code, nm or title, "grouplinksforyou:" + title[:60])
print("after feed, pool size:", len(pool))

# --- D. grouplink_intl: 34 codes; names from nearby heading/list text
gi = load("grouplink_intl")
for m in re.finditer(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", gi):
    code = m.group(1)
    ctx = gi[max(0, m.start()-600):m.start()]
    # last <h2>/<h3>/<li> text before link
    tails = re.findall(r"<(?:h[23]|li|strong|b)>([^<]{2,100})</(?:h[23]|li|strong|b)>", ctx)
    nm = html.unescape(tails[-1]).strip() if tails else ""
    add(code, nm, "grouplink_intl")
print("after grouplink_intl, pool:", len(pool))

# --- D2. techsslash_ph
ts = load("techsslash_ph")
for m in re.finditer(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", ts):
    code = m.group(1)
    ctx = ts[max(0, m.start()-600):m.start()]
    tails = re.findall(r"<(?:h[23]|li|strong|b)>([^<]{2,100})</(?:h[23]|li|strong|b)>", ctx)
    nm = html.unescape(tails[-1]).strip() if tails else ""
    add(code, nm, "techsslash_ph")
print("after techsslash, pool:", len(pool))

# --- E. groupwa pages: wagd cards
for key in ["groupwa_jobs", "groupwa_education", "groupwa_gaming"]:
    b = load(key)
    for m in re.finditer(r'data-name="([^"]*)"[^>]*data-cat="([^"]*)"[^>]*data-desc="([^"]*)"[^>]*data-link="https://chat\.whatsapp\.com/([A-Za-z0-9]{22})"', b):
        add(m.group(4), html.unescape(m.group(1)), key)
    # also plain links
    for m in re.finditer(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", b):
        add(m.group(1), "", key)
print("after groupwa, pool:", len(pool))

# --- C. shopee bit.ly table: name + member count + bit.ly
s = load("tls_shopee")
rows = re.findall(r"<tr><td>(.*?)</td><td>(\d+)</td><td>(bit\.ly/[A-Za-z0-9_-]+)</td></tr>", s)
print("shopee rows:", len(rows))
shopee = []
for nm, cnt, bl in rows:
    nm = html.unescape(re.sub(r"<[^>]+>", "", nm)).strip()
    shopee.append({"name": nm, "members": cnt, "bitly": "https://" + bl})
json.dump(shopee, open(WAVE + "team32_shopee_rows.json", "w"), indent=1, ensure_ascii=False)

json.dump(list(pool.values()), open(WAVE + "team32_pool_raw.json", "w"), indent=1, ensure_ascii=False)
print("POOL total:", len(pool))
for c in sorted(pool.values(), key=lambda x: x["source"]):
    print(f"  {c['code']} | {c['source'][:40]:40s} | {c['name'][:70]}")
