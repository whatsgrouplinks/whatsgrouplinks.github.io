"""Team 13: re-fetch all 168 appgrouplink listing pages (sitemap identical to Nov 4,
but content rotates), parse (name, code) pairs. Incremental save to team13_state/ag_raw.json."""
import requests, re, time, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor

WORK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
from team18_pages import PAGES

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = os.path.join(WORK, "ag_raw.json")
lock = threading.Lock()

def load_existing():
    if os.path.exists(OUT):
        return json.load(open(OUT))
    return {"pages": {}}

state = load_existing()

def fetch_one(url):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*",
                      "Accept-Language": "en-US,en;q=0.9"})
    for attempt in range(3):
        try:
            r = s.get(url, timeout=60)
            if r.status_code == 200 and len(r.text) > 5000:
                return r.text
            time.sleep(4 + attempt * 5)
        except Exception:
            time.sleep(5 + attempt * 5)
    return None

def parse(html):
    pairs = []
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I):
        row = m.group(1)
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)
        if len(cells) >= 2:
            name = re.sub(r'<[^>]+>', '', cells[0]).strip()
            hm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', row)
            if name and hm and 'Group Name' not in name:
                pairs.append([name, hm.group(1)])
    if not pairs:
        for m in re.finditer(r'href="(https://chat\.whatsapp\.com/(?:invite/)?[A-Za-z0-9]{20,24})"[^>]*>[^<]*Join', html, re.I):
            pairs.append(["", m.group(1).split("/")[-1]])
    return pairs

def worker(url):
    slug = url.rstrip("/").split("/")[-1]
    with lock:
        if slug in state["pages"] and state["pages"][slug].get("pairs"):
            return "cached %d" % len(state["pages"][slug]["pairs"])
    html = fetch_one(url)
    with lock:
        if html:
            state["pages"][slug] = {"url": url, "pairs": parse(html)}
            json.dump(state, open(OUT, "w"))
            return "ok %s %d" % (slug, len(state["pages"][slug]["pairs"]))
        else:
            state["pages"][slug] = {"url": url, "pairs": [], "fetch_failed": True}
            json.dump(state, open(OUT, "w"))
            return "fail %s" % slug

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(worker, u): u for u in PAGES}
        for f in futs:
            try:
                print(f.result(), flush=True)
            except Exception as e:
                print("ERR", futs[f], e, flush=True)
    print("DONE pages=%d total_pairs=%d" % (
        len(state["pages"]),
        sum(len(v.get("pairs", [])) for v in state["pages"].values())), flush=True)
