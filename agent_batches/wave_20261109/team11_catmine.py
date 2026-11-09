#!/usr/bin/env python3
"""Team 11: mine groupsinvite.link category pages for unharvested entries.
Fetch each /group/category/<slug>/ page once via curl, extract /group/link/<slug>/
slugs, compare against the Nov 8 enumeration (2671). New slugs -> team11_cat_new_slugs.json."""
import json, os, re, subprocess, time
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CATS = ["ai-machine-learning-data-science","astrology-horoscope-spirituality","beauty-fashion-lifestyle","business-startup-earn-money","buy-sell-marketplace","career-jobs-freelancing","community-friendship-social","crypto-blockchain-web3","dating-matrimony-relationships","education-study-learning","entertainment-comedy-fun","finance-stocks-investing","fitness-gym-bodybuilding","local-city-country","marketing-advertising-affiliate","music-songs-bands","news-politics-information","photography-video-editing","programming-coding-software","religion-devotional-faith","science-engineering-technology","shopping-deals-coupons","sports-games-fantasy","art-drawing-crafts","hobbies-diy-home-projects","animals-pets-wildlife","automotive-cars-bikes","cooking-food-recipes","gardening-farming-agriculture","travel-adventure-road-trips","real-estate-property-housing","movies-tv-celebrities","books-ebooks-literature"]
enum = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team13_state/gi_enum.json"))
SLUG_RE = re.compile(r'/group/link/([A-Za-z0-9]+)/')
found = {}
for cat in CATS:
    url = "https://groupsinvite.link/group/category/%s/" % cat
    tmp = "/tmp/team11_cat.html"
    try:
        r = subprocess.run(["curl","-sL","--max-time","30","-A",UA,"-o",tmp,"-w","%{http_code}",url], capture_output=True, text=True, timeout=40)
        body = open(tmp, encoding="utf-8", errors="ignore").read() if os.path.exists(tmp) else ""
        slugs = sorted(set(SLUG_RE.findall(body)))
        new = [s for s in slugs if s not in enum]
        found[cat] = {"http": r.stdout.strip(), "bytes": len(body), "slugs": len(slugs), "new": new}
        print(cat, r.stdout.strip(), "bytes", len(body), "slugs", len(slugs), "new", len(new), flush=True)
    except Exception as e:
        found[cat] = {"error": str(e)}
        print(cat, "ERR", e, flush=True)
    time.sleep(1.0)
json.dump(found, open(os.path.join(WAVE, "team11_cat_slugs.json"), "w"), indent=1)
allnew = sorted({s for v in found.values() for s in v.get("new", [])})
json.dump(allnew, open(os.path.join(WAVE, "team11_cat_new_slugs.json"), "w"))
print("TOTAL categories:", len(CATS), "TOTAL new slugs not in enum:", len(allnew))
