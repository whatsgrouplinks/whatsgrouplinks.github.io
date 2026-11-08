#!/usr/bin/env python3
"""team32 repair: re-fetch og:title for all verified codes, decode entities FIRST,
then truncate on decoded text, rebuild descriptions. Fixes mid-entity truncation."""
import json, re, html, os, time
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106/'
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
CAT_DESC = {
 "sports": "sports fans group for live scores, match updates and cricket and football discussions",
 "entertainment": "entertainment group for movies, web series and trending videos",
 "community-social": "community group for Pakistanis to chat, share updates and connect",
 "news": "news group for the latest Pakistan news updates and breaking headlines",
 "friendship": "friendship group to meet new friends, chat daily and share good company",
 "funny": "funny group for jokes, memes and hilarious videos to brighten your day",
}

def fetch_title(code):
    try:
        r = requests.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=30)
        if r.status_code != 200:
            return (code, None)
        m = OG_RE.search(r.text)
        if not m or not m.group(1).strip():
            return (code, None)
        return (code, html.unescape(m.group(1).strip()))
    except Exception:
        return (code, None)

def clean_tail(s):
    # strip a trailing partial entity left by an old truncation
    s = re.sub(r'&(?:#[xX]?[0-9a-fA-F]*|[a-zA-Z]*)$', '', s)
    return s.strip()

def main():
    v = json.load(open(WAVE + 'team32-p13-listicles-sports-movies.json'))
    print("loaded", len(v), flush=True)
    codes = [x['invite'].split('/')[-1] for x in v]
    titles = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, (code, title) in enumerate(ex.map(fetch_title, codes)):
            if title:
                titles[code] = title
            if (i+1) % 50 == 0:
                print(f"refetched {i+1}/{len(codes)} ok={len(titles)}", flush=True)
    print(f"refetch ok={len(titles)} failed={len(codes)-len(titles)}", flush=True)
    fixed = 0
    for x in v:
        code = x['invite'].split('/')[-1]
        title = titles.get(code)
        if title:
            name = title[:100]
            desc_core = CAT_DESC.get(x['category'], "community group to chat and share updates")
            desc = f"Join {name}, an active WhatsApp {desc_core}. Connect with members, share updates and enjoy daily discussions in this {x['category']} group."
            if len(desc) > 300:
                desc = desc[:300].rsplit(' ', 1)[0]
            x['name'] = name
            x['description'] = desc
            fixed += 1
        else:
            # keep entry, just clean partial-entity tails
            x['name'] = clean_tail(html.unescape(x['name']))[:100]
            x['description'] = clean_tail(html.unescape(x['description']))[:300]
    json.dump(v, open(WAVE + 'team32-p13-listicles-sports-movies.json', 'w'), ensure_ascii=False, indent=1)
    print(f"rebuilt {fixed}/{len(v)} from fresh og:title; wrote file", flush=True)

if __name__ == "__main__":
    main()
