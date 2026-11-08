#!/usr/bin/env python3
"""team32 verifier: check chat.whatsapp.com codes, og:title non-empty = LIVE.
Dead (200 + empty og:title) dropped. Transport failures -> pending (retry once after 60s).
Writes verified/pending incrementally so a wipe cannot lose everything."""
import json, re, time, sys, html, os
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106/'
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
PORN_RE = re.compile(r'porn|pornhub|xxx|nudes?|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob', re.I)
SCAM_RE = re.compile(r'receiver and loader|money mule|double (your|the) (money|investment)|counterfeit (currency|money|notes)|buy (drugs|weed|cocaine|heroin)', re.I)

CAT_DESC = {
 "sports": "sports fans group for live scores, match updates and cricket and football discussions",
 "entertainment": "entertainment group for movies, web series and trending videos",
 "community-social": "community group for Pakistanis to chat, share updates and connect",
 "news": "news group for the latest Pakistan news updates and breaking headlines",
 "friendship": "friendship group to meet new friends, chat daily and share good company",
 "funny": "funny group for jokes, memes and hilarious videos to brighten your day",
}
JUNK_TOK = re.compile(r'(target=|href=|class=|rel=|nofollow|_blank|kb-|kt-|section|overlay|button|div|span)', re.I)

def clean_pending_name(nm, cat):
    nm = re.sub(r'<[^>]+>', ' ', html.unescape(nm or ''))
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'\b(Join Group|Join Chat|Click Here|Join Now|Join In|Join|Link)\b', ' ', nm, flags=re.I)
    nm = re.sub(r'\s+', ' ', nm).strip(' -|•·»«›<>')
    if not nm or len(nm) < 3 or JUNK_TOK.search(nm):
        return f"{cat.title()} WhatsApp Group"
    return nm[:100]

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code != 200:
            return (code, "transport", f"HTTP {r.status_code}", "")
        m = OG_RE.search(r.text)
        title = (m.group(1).strip() if m else "")
        title = title.replace("&amp;", "&").replace("&quot;", '"').replace("&#x27;", "'").replace("&lt;", "<").replace("&gt;", ">")
        if title:
            return (code, "live", title, "")
        return (code, "dead", "", "")
    except requests.exceptions.RequestException as e:
        return (code, "transport", str(e)[:100], "")

def build_outputs(live, transport, by_code):
    verified, pending = [], []
    for code, title in live.items():
        c = by_code[code]
        name = title.strip()
        if PORN_RE.search(name) or SCAM_RE.search(name):
            continue
        cat = c["category"]
        country = c["country"]
        if country == "International":
            if re.search(r'\b(pakistan|pakistani|lahore|karachi|islamabad)\b', title, re.I):
                country = "PK"
            elif re.search(r'\bindia(n)?\b|mumbai|delhi|chennai', title, re.I):
                country = "IN"
        desc_core = CAT_DESC.get(cat, "community group to chat and share updates")
        desc = f"Join {name}, an active WhatsApp {desc_core}. Connect with members, share updates and enjoy daily discussions in this {cat} group."
        verified.append({"name": name[:100], "category": cat, "country": country,
                         "description": desc[:300], "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
    for code in transport:
        c = by_code[code]
        pending.append({"code": code, "name": clean_pending_name(c["name"], c["category"]), "category": c["category"],
                        "country": c["country"], "invite": f"https://chat.whatsapp.com/{code}"})
    json.dump(verified, open(WAVE + 'team32-p13-listicles-sports-movies.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + 'team32-p13-listicles-sports-movies-pending.json', 'w'), ensure_ascii=False, indent=1)
    return len(verified), len(pending)

def main():
    cands = json.load(open(os.path.join(BASE, 'candidates.json')))
    print("candidates:", len(cands), flush=True)
    by_code = {c["code"]: c for c in cands}
    codes = list(by_code)
    live, dead, transport = {}, [], []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, (code, status, info, _) in enumerate(ex.map(check, codes)):
            if status == "live":
                live[code] = info
            elif status == "dead":
                dead.append(code)
            else:
                transport.append(code)
            if (i+1) % 50 == 0:
                print(f"checked {i+1}/{len(codes)} live={len(live)} dead={len(dead)} transport={len(transport)}", flush=True)
                v, p = build_outputs(live, transport, by_code)
                print(f"  checkpoint written: verified={v} pending={p}", flush=True)
    print(f"pass1: live={len(live)} dead={len(dead)} transport={len(transport)}", flush=True)
    if transport:
        print("sleeping 60s before transport retry...", flush=True)
        time.sleep(60)
        retry = list(transport)
        transport = []
        with ThreadPoolExecutor(max_workers=4) as ex:
            for code, status, info, _ in ex.map(check, retry):
                if status == "live":
                    live[code] = info
                elif status == "dead":
                    dead.append(code)
                else:
                    transport.append(code)
        print(f"after retry: live={len(live)} dead={len(dead)} transport={len(transport)}", flush=True)
    v, p = build_outputs(live, transport, by_code)
    print(f"WROTE verified={v} pending={p} dead={len(dead)}", flush=True)

if __name__ == "__main__":
    main()
