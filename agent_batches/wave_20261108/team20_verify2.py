import requests, re, json, time, html, os
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
GENERIC = {"whatsapp group", "join this group on whatsapp", "whatsapp", "join group on whatsapp"}
DROP_SUB = ["betway","betting","casino","forex","crypto","binance","bitcoin","coin earning","ebl","nadra","adult","porn","xxx","escort","call girl","salt money","airdrops","airdrop","ustd","mine and earn","signals","trading","investment","seagul","unixrave","angel 42","paid parmotion","thunder tricks","all services here","links group","global pakistan","reseller","smm panel","quran","hadees","taleem-e-rasool","ramadhan","novels","psl","ipl","cricket","ptv sport","geo pakistan","pak army","pak armed","pti pakistan","zindabad","viral funny","super masti","dard e dil","the boys","daily quotes","wholesale","buy sale","online shopping","sunset brownies","property booster","islamic shia","urdu adab","shayari","mushal","dastan","aakhri","deen seekhen","muslim league","rizvi sher","online business","cashbep","refer to refer","guaranteed work","the index points","is not functioning"]
GARBAGE = {"", "♥️", ") –", "app", "free", "–", ":", "??", "????", "the boys"}

def keep(c):
    n = c["name_raw"].strip().lower()
    n2 = re.sub(r'[^a-z0-9 ]', ' ', n)
    if n in GARBAGE or len(n) < 2: return False
    for d in DROP_SUB:
        if d in n2 or d in n: return False
    return True

cands = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_candidates.json"))
# manual drops
manual_drop = {"J9PwCQzRUPK9OglUaGJ2fd", "KVWGww5vHrlAbnFsGaq3Wz", "GuyhfJ9wqdpJuknoZ5lJju",
 "FE7l37sw0maGMUrs0GOC7F", "L6RPOzqjrLLB4CkawvuDyA", "DOCKnbqq32m1CCwhlGBO3Z"}
kept, dropped = [], []
for c in cands:
    if c["code"] in manual_drop or not keep(c):
        dropped.append(c)
    else:
        kept.append(c)
print("candidates:", len(cands), "kept:", len(kept), "dropped:", len(dropped), flush=True)
json.dump(kept, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_tokeep.json","w"), ensure_ascii=False, indent=1)
json.dump(dropped, open("/home/hatch/workspace/groups-site/agent_batches/wave_20261108/team20_dropped.json","w"), ensure_ascii=False, indent=1) if False else json.dump(dropped, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_dropped.json","w"), ensure_ascii=False, indent=1)
for c in dropped: print("DROP", c["code"], "|", c["name_raw"][:60], flush=True)

def check(c):
    code = c["code"]
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in (1, 2):
        try:
            s = requests.Session()
            r = s.get(url, headers=UA, timeout=25)
            m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', r.text, re.I)
            if not m:
                m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', r.text, re.I)
            title = html.unescape(m.group(1)).strip() if m else ""
            if r.status_code == 200 and title and title.lower() not in GENERIC:
                return {"code": code, "status": "live", "og_title": title, "http": r.status_code,
                        "name_raw": c["name_raw"], "src": c["src"], "cat_hint": c["cat_hint"]}
            if r.status_code == 200 and not title:
                if attempt == 1:
                    time.sleep(4); continue
                return {"code": code, "status": "dead", "og_title": "", "http": r.status_code, "note": "200-empty-after-retry",
                        "name_raw": c["name_raw"], "src": c["src"], "cat_hint": c["cat_hint"]}
            return {"code": code, "status": "dead", "og_title": title, "http": r.status_code,
                    "name_raw": c["name_raw"], "src": c["src"], "cat_hint": c["cat_hint"]}
        except Exception as e:
            if attempt == 1:
                time.sleep(4); continue
            return {"code": code, "status": "pending", "og_title": "", "http": 0, "note": f"transport:{type(e).__name__}",
                    "name_raw": c["name_raw"], "src": c["src"], "cat_hint": c["cat_hint"]}

import threading
lock = threading.Lock()
results = []
def run(c):
    time.sleep(0.6 * (hash(c["code"]) % 3))
    r = check(c)
    with lock:
        results.append(r)
        json.dump(results, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_verified.json","w"), ensure_ascii=False, indent=1)
        print(len(results), "/", len(kept), r["code"], r["status"], repr(r["og_title"][:60]), flush=True)

with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(run, kept))
from collections import Counter
print(Counter(r["status"] for r in results), flush=True)
