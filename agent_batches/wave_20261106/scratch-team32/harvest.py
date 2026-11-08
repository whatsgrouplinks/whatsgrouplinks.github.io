#!/usr/bin/env python3
"""team32 harvest (combined): parallel fetch of listicle pages, extract chat.whatsapp.com codes."""
import json, re, html, os
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

URLS = [
 ("https://whatgroups.com/cricket-whatsapp-group-links/", "sports", "International"),
 ("https://minidea.co.in/cricket-whatsapp-group-link/", "sports", "IN"),
 ("https://grouplink.com.in/active-sports-whatsapp-group-links-2026/", "sports", "International"),
 ("https://newgrouplinks.pk/cricket-whatsapp-group-links/", "sports", "PK"),
 ("https://wglfinder.com/cricket-whatsapp-group-link/", "sports", "International"),
 ("https://appgrouplink.com/cricket-whatsapp-group-links/", "sports", "International"),
 ("https://wagroupshub.com/", "entertainment", "International"),
 ("https://groupwa.link/", "entertainment", "International"),
 ("https://www.whtsagrouplinks.com", "entertainment", "International"),
 ("https://whtsgrouplink.com", "entertainment", "International"),
 ("https://whatzgrouplink.com", "entertainment", "International"),
 ("https://www.whtsagrouplinks.com/movies-whatsapp-group-link/", "entertainment", "International"),
 ("https://whtsgrouplink.com/movies-whatsapp-group-links/", "entertainment", "International"),
 ("https://wahublink.com/sports-whatsapp-group-links/", "sports", "International"),
 ("https://www.whtsagrouplinks.com/sports-whatsapp-group-links/", "sports", "International"),
 ("https://wagroupshub.com/sports-whatsapp-group-links/", "sports", "International"),
 ("https://whatstele.com/whatsapp/group-links/pakistani/", "community-social", "PK"),
 ("http://grouplink.com.in/pakistan-whatsapp-group-links/", "community-social", "PK"),
 ("https://www.whtsagrouplinks.com/pakistani-whatsapp-group-link/", "community-social", "PK"),
 ("https://grouplink.com.in/pakistani-news-whatsapp-group-links/", "news", "PK"),
 ("https://whatgroups.com/whatsapp-group-links-pakistan/", "community-social", "PK"),
 ("https://www.grouplinksforyou.com/2023/03/1000-active-pakistani-whatsapp-group.html", "community-social", "PK"),
 ("https://newgrouplinks.pk/friendship-whatsapp-group-links/", "friendship", "PK"),
 ("https://wahublink.com/entertainment-whatsapp-group-links/", "entertainment", "International"),
 ("https://whatstele.com/whatsapp/group-links/memes-stickers/", "funny", "International"),
 ("https://activewagroup.com/pakistani-whatsapp-group-links/", "community-social", "PK"),
 ("https://grouplink.com.in/1000-best-jokers-whatsapp-group-links/", "funny", "International"),
 ("https://whtspgrouplink.com/", "entertainment", "International"),
 ("https://whatsgroupslinkspk.com/", "entertainment", "PK"),
 ("https://www.whtsagrouplinks.com/friendship-whatsapp-group-links/", "friendship", "International"),
 ("https://whtspgrouplink.com/foreign-friends-whatsapp-group-links/", "friendship", "International"),
]

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{22})(?![A-Za-z0-9_-])')
PORN_RE = re.compile(r'porn|pornhub|xxx|nudes?|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob', re.I)

def clean_name(raw):
    raw = html.unescape(raw)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    raw = re.sub(r'\s+', ' ', raw).strip()
    raw = raw[-100:]
    for junk in ["Join Group", "Join Chat", "Click Here", "Click to Join", "Join Now", "Join In", "Join"]:
        raw = re.sub(r'\b' + re.escape(junk) + r'\b', ' ', raw, flags=re.I)
    raw = re.sub(r'\s+', ' ', raw).strip(' -|•·»«›<>')
    return raw[:100]

def fetch(item):
    url, cat, country = item
    try:
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code != 200:
            return (url, cat, country, [], r.status_code)
        out = []
        for m in CODE_RE.finditer(r.text):
            out.append({"code": m.group(1), "name": clean_name(r.text[max(0, m.start()-700):m.start()]),
                        "category": cat, "country": country, "source": url})
        return (url, cat, country, out, r.status_code)
    except Exception as e:
        return (url, cat, country, [], f"ERR {str(e)[:80]}")

def main():
    union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106/dedupe_union.json')))
    found = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for url, cat, country, items, status in ex.map(fetch, URLS):
            n_new = 0
            for it in items:
                if it["code"] in union or it["code"] in found:
                    continue
                if PORN_RE.search(it["name"] or ""):
                    continue
                found[it["code"]] = it
                n_new += 1
            print(f"{status} {url} codes={len(items)} new={n_new} total={len(found)}", flush=True)
    json.dump(list(found.values()), open(os.path.join(BASE, 'candidates.json'), 'w'), ensure_ascii=False, indent=1)
    print("WROTE candidates:", len(found), flush=True)

if __name__ == "__main__":
    main()
