#!/usr/bin/env python3
"""Team04 step1: fetch 71 listing pages, extract card data -> team04_scratch/cards.json"""
import requests, re, json, time, sys, html
from concurrent.futures import ThreadPoolExecutor

BASE = "https://groupchatconnect.info"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def fetch(p):
    s = requests.Session(); s.headers.update({"User-Agent": UA})
    for attempt in range(3):
        try:
            r = s.get(f"{BASE}/?page={p}", timeout=40)
            if r.status_code == 200:
                return p, r.text
        except Exception as e:
            time.sleep(2 + attempt * 3)
    return p, None

def parse_cards(h):
    cards = []
    # split on group-info blocks
    for m in re.finditer(r'<div class="group-info flex-grow-1">(.*?)</div>\s*</div>', h, re.S):
        b = m.group(1)
        am = re.search(r'<a href="/groupe/(\d+)"[^>]*>(.*?)</a>', b, re.S)
        if not am: continue
        gid = am.group(1)
        name = html.unescape(re.sub(r'<[^>]+>', '', am.group(2))).strip()
        badges = [html.unescape(x).strip() for x in re.findall(r'<i class="fas fa-(tag|globe|language)[^>]*></i>\s*([^<]+?)\s*</span>', b)]
        # badge order: (icon, text)
        cat = country = lang = ""
        for icon, text in badges:
            if icon == 'tag': cat = text
            elif icon == 'globe': country = text
            elif icon == 'language': lang = text
        plus18 = 'bg-danger">+18' in b or '>+18<' in b
        dm = re.search(r'<p class="card-text[^"]*"[^>]*>(.*?)</p>', b, re.S)
        desc = html.unescape(re.sub(r'<[^>]+>', ' ', dm.group(1))).strip() if dm else ""
        cards.append({"id": gid, "name": name, "cat_ar": cat, "country_ar": country,
                      "lang_ar": lang, "plus18": plus18, "card_desc": re.sub(r'\s+', ' ', desc)[:500]})
    return cards

def main():
    pages = list(range(1, 72))
    all_cards, seen = {}, {}
    fails = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for p, h in ex.map(fetch, pages):
            if h is None:
                fails.append(p); continue
            cs = parse_cards(h)
            for c in cs:
                if c["id"] not in seen:
                    seen[c["id"]] = True
                    all_cards[c["id"]] = c
            print(f"page {p}: {len(cs)} cards", flush=True)
    print("TOTAL unique:", len(all_cards), "failed pages:", fails)
    json.dump({"cards": list(all_cards.values()), "failed_pages": fails},
              open("team04_scratch/cards.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # vocab dump
    from collections import Counter
    print("CATS:", Counter(c["cat_ar"] for c in all_cards.values()))
    print("COUNTRIES:", Counter(c["country_ar"] for c in all_cards.values()))

if __name__ == "__main__":
    main()
