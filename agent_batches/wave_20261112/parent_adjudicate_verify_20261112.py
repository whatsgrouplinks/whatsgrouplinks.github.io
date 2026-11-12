#!/usr/bin/env python3
"""Parent adjudication + spot-verification for wave 20261112.
1. Drop the 123 casino/slots signal-platform groups flagged by the coordinator
   (betting-promo screen precedent: Nov 11 dropped BETS1GREEN sports-betting
   recruitment; team10 dropped 'Divulgacao De Plataformas' at team level).
2. Spot-verify 35 random parent-clean codes via live og:title (og:description
   is generic on live AND dead pages - never a live signal).
"""
import json, random, re, time, sys
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
BUILD = "/home/hatch/workspace/whatsapp-groups-site/"

clean = json.load(open(WAVE + "wave_20261112_clean.json"))
flagged = json.load(open(WAVE + "team05-casino-flagged.json"))
flag_codes = {f["code"] for f in flagged}
print("clean:", len(clean), "casino-flagged:", len(flag_codes))

parent_clean = [c for c in clean if c["invite"].rstrip("/").split("/")[-1] not in flag_codes]
dropped = [c for c in clean if c["invite"].rstrip("/").split("/")[-1] in flag_codes]
print("parent clean:", len(parent_clean), "dropped:", len(dropped))
assert len(parent_clean) + len(dropped) == len(clean)
assert len({c["invite"] for c in parent_clean}) == len(parent_clean)
not_in_clean = [c for c in flag_codes if c not in {x["invite"].rstrip("/").split("/")[-1] for x in clean}]
print("flagged codes NOT in clean (already excluded upstream):", len(not_in_clean), not_in_clean)
json.dump({"dropped_count": len(dropped), "flagged_not_in_clean": not_in_clean},
          open(WAVE + "wave_20261112_casino_adjudication.json", "w"), ensure_ascii=False)
json.dump(parent_clean, open(WAVE + "wave_20261112_clean_parent.json", "w"), ensure_ascii=False)
json.dump(dropped, open(WAVE + "wave_20261112_casino_dropped.json", "w"), ensure_ascii=False)
json.dump(flagged, open(WAVE + "wave_20261112_casino_flagged.json", "w"), ensure_ascii=False)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)

def og_title(sess, code):
    try:
        r = sess.get("https://chat.whatsapp.com/" + code, headers=UA, timeout=60)
        if r.status_code != 200:
            return None, r.status_code
        m = TITLE_RE.search(r.text)
        if not m:
            return "", r.status_code
        import html as h
        return h.unescape(m.group(1)).strip(), r.status_code
    except Exception as e:
        return None, str(e)

sess = requests.Session()
# Controls
groups = json.load(open(BUILD + "groups.json"))
live_code = groups[0]["invite"].rstrip("/").split("/")[-1]
t, s = og_title(sess, live_code)
print("CONTROL known-live:", live_code, "->", repr(t)[:80], "http", s)
assert t, "control live failed"
t2, s2 = og_title(sess, "ZZZZZZZZZZZZZZZZZZZZZZ")
print("CONTROL fabricated:", repr(t2)[:80], "http", s2)
assert not t2, "control fabricated unexpectedly live"

random.seed(20261112)
sample = random.sample(parent_clean, 35)
results = []
for i, item in enumerate(sample):
    code = item["invite"].rstrip("/").split("/")[-1]
    t, s = og_title(sess, code)
    if t == "":
        time.sleep(15)
        t, s = og_title(sess, code)
    live = bool(t)
    results.append({"code": code, "name": item["name"], "live": live, "title": t, "http": s})
    print(f"{i+1:2d} {'LIVE' if live else 'DEAD'} {code} {item['name'][:50]!r} title={t[:60]!r}")
live_n = sum(r["live"] for r in results)
print(f"SPOT-VERIFY: {live_n}/35 live")
json.dump({"controls": {"live_code": live_code, "live_title": t, "fabricated_title": t2},
           "sample": results, "live": live_n, "total": 35},
          open(WAVE + "parent_verify_state_20261112.json", "w"), ensure_ascii=False)
dead = [r for r in results if not r["live"]]
if dead:
    print("DEAD IN SAMPLE:", dead)
    sys.exit(2)
print("PARENT VERIFY OK")
