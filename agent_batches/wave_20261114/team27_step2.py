#!/usr/bin/env python3
"""team27 step2: mine target listing pages, extract (name, code), dedupe vs union."""
import requests, re, json, html, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
S = requests.Session(); S.headers.update(UA)

PAGES = [
 ("https://wahublink.com/gaming-whatsapp-group-links/", "Gaming", ""),
 ("https://wahublink.com/poetry-whatsapp-group-links/", "Poetry", ""),
 ("https://wahublink.com/movies-whatsapp-group-links/", "Entertainment", ""),
 ("https://wahublink.com/online-shopping-whatsapp-group-links/", "Buy Sell", ""),
 ("https://wahublink.com/indian-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://wahublink.com/pakistani-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://wahublink.com/uk-whatsapp-group-links/", "Community & Social", "GB"),
 ("https://wahublink.com/usa-whatsapp-group-links/", "Community & Social", "US"),
 ("https://wahublink.com/uae-dubai-whatsapp-group-links/", "Community & Social", "AE"),
 ("https://wagroupshub.com/business-whatsapp-group-links/", "Business", ""),
 ("https://wagroupshub.com/entertainment-whatsapp-group-links/", "Entertainment", ""),
 ("https://wagroupshub.com/news-whatsapp-group-links/", "News", ""),
 ("https://wagroupshub.com/poetry-whatsapp-group-links/", "Poetry", ""),
 ("https://wagroupshub.com/movies-whatsapp-group-links/", "Entertainment", ""),
 ("https://wagroupshub.com/online-shopping-whatsapp-group-links/", "Buy Sell", ""),
 ("https://wagroupshub.com/tamil-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://wagroupshub.com/kerala-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://wagroupshub.com/malayalam-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://wagroupshub.com/sri-lanka-whatsapp-group-links/", "Community & Social", "LK"),
 ("https://wagroupshub.com/uk-whatsapp-group-links/", "Community & Social", "GB"),
 ("https://wagroupshub.com/usa-whatsapp-group-links/", "Community & Social", "US"),
 ("https://wagroupshub.com/youtube-whatsapp-group-links/", "Entertainment", ""),
 ("https://activewagroup.com/business-whatsapp-group-links/", "Business", ""),
 ("https://activewagroup.com/entertainment-whatsapp-group-links/", "Entertainment", ""),
 ("https://activewagroup.com/news-whatsapp-group-links/", "News", ""),
 ("https://activewagroup.com/online-earning-whatsapp-group-links/", "Earning", ""),
 ("https://activewagroup.com/online-shopping-whatsapp-group-links/", "Buy Sell", ""),
 ("https://activewagroup.com/poetry-whatsapp-group-links/", "Poetry", ""),
 ("https://activewagroup.com/sports-whatsapp-group-links/", "Sports", ""),
 ("https://activewagroup.com/single-girls-whatsapp-group-links/", "Community & Social", ""),
 ("https://activewagroup.com/uk-whatsapp-group-links/", "Community & Social", "GB"),
 ("https://activewagroup.com/usa-whatsapp-group-links/", "Community & Social", "US"),
 ("https://activewagroup.com/pakistani-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://activewagroup.com/tamil-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://activewagroup.com/sri-lanka-whatsapp-group-links/", "Community & Social", "LK"),
 ("https://activewagroup.com/kerala-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://activewagroup.com/malayalam-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://newgrouplinks.pk/business-whatsapp-group-links/", "Business", "PK"),
 ("https://newgrouplinks.pk/karachi-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://newgrouplinks.pk/lahore-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://newgrouplinks.pk/pakistani-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://newgrouplinks.pk/youtube-whatsapp-group-links/", "Entertainment", "PK"),
 ("https://grouplink.com.in/category/business/", "Business", "IN"),
 ("https://grouplink.com.in/category/online-earning/", "Earning", "IN"),
 ("https://grouplink.com.in/2900-active-indian-business-group-links/", "Business", "IN"),
 ("https://wagroupslink.com/indian-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://wagroupslink.com/pakistani-whatsapp-group-link/", "Community & Social", "PK"),
 ("https://wagroupslink.com/all-group-links/", "Community & Social", ""),
]

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
print("union size", len(union))

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"\s+", " ", s).strip(" |-\u2013\u2014")
    return s

def extract(text):
    """Return list of (name, code). Table rows first, then generic fallback."""
    out = []
    # table rows: <tr><td>NAME</td><td><a href="...chat.whatsapp.com/CODE"
    for m in re.finditer(r"<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", text, re.S):
        out.append((clean(m.group(1)), m.group(2)))
    seen = {c for _, c in out}
    # generic: any chat link; name = last text chunk before link within 400 chars
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,30})', text):
        code = m.group(1)
        if code in seen: continue
        seg = text[max(0, m.start()-500):m.start()]
        seg = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", seg, flags=re.S)
        txt = clean(seg)
        # name heuristic: last 6 words before link, strip boilerplate
        name = txt.split("Join")[-1].strip()
        words = name.split()
        name = " ".join(words[-6:]) if words else ""
        if len(name) < 2: name = ""
        out.append((name, code)); seen.add(code)
    return out

results, tried = [], []
raw_total = 0
for url, cat, country in PAGES:
    try:
        r = S.get(url, timeout=60)
        status = r.status_code
        pairs = extract(r.text) if status == 200 else []
    except Exception as e:
        status, pairs = f"ERR {e}", []
    raw_total += len(pairs)
    fresh = 0
    for name, code in pairs:
        if code not in union:
            results.append({"name": name, "category": cat, "country": country,
                            "code": code, "source_page": url})
            fresh += 1
    tried.append({"url": url, "category": cat, "country": country, "status": status,
                  "codes_found": len(pairs), "fresh_vs_union": fresh})
    print(f"{status} {len(pairs):4d} fresh={fresh:3d} {url}")
    time.sleep(1)

# dedupe within team (keep first)
dedup, seen = [], set()
for it in results:
    if it["code"] in seen: continue
    seen.add(it["code"]); dedup.append(it)
print(f"raw={raw_total} fresh_vs_union={len(results)} fresh_unique={len(dedup)}")
json.dump({"tried": tried, "fresh": dedup},
          open("team27-raw.json", "w"), indent=1, ensure_ascii=False)
