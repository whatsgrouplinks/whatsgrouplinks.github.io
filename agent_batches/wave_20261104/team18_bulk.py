"""Team 18 bulk fetch: all appgrouplink.com listing pages -> (name, code) pairs.
Saves incrementally to team18_raw.json. Run in background."""
import requests, re, time, json, os, threading
from concurrent.futures import ThreadPoolExecutor

WORK = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, WORK)
from team18_pages import PAGES

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = os.path.join(WORK, "team18_raw.json")
RAWDIR = os.path.join(WORK, "team18_raw_html")
os.makedirs(RAWDIR, exist_ok=True)
lock = threading.Lock()

def load_existing():
    if os.path.exists(OUT):
        d = json.load(open(OUT))
        return d
    return {"pages": {}}

state = load_existing()

def fetch_one(url):
    slug = url.rstrip("/").split("/")[-1]
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*",
                      "Accept-Language": "en-US,en;q=0.9"})
    for attempt in range(4):
        try:
            r = s.get(url, timeout=110)
            if r.status_code == 200 and len(r.text) > 5000:
                return r.text
            time.sleep(3 + attempt * 4)
        except Exception:
            time.sleep(5 + attempt * 5)
    return None

def parse(html):
    pairs = []
    # table rows: <tr>...<td>name</td>...<a href="chat.whatsapp.com/invite/CODE">
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I):
        row = m.group(1)
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)
        if len(cells) >= 2:
            name = re.sub(r'<[^>]+>', '', cells[0]).strip()
            hm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', row)
            if name and hm and 'Group Name' not in name:
                pairs.append([name, hm.group(1)])
    if not pairs:
        # fallback: any invite href near Join In anchors
        for m in re.finditer(r'href="(https://chat\.whatsapp\.com/(?:invite/)?[A-Za-z0-9]{20,24})"[^>]*>[^<]*Join', html, re.I):
            pairs.append(["", m.group(1).split("/")[-1]])
    return pairs

def worker(url):
    slug = url.rstrip("/").split("/")[-1]
    with lock:
        if slug in state["pages"]:
            return "cached"
    html = fetch_one(url)
    with lock:
        if html:
            state["pages"][slug] = {"url": url, "pairs": parse(html)}
            try:
                open(os.path.join(RAWDIR, slug + ".html"), "w").write(html)
            except Exception:
                pass
            json.dump(state, open(OUT, "w"))
            return "ok %d" % len(state["pages"][slug]["pairs"])
        else:
            state["pages"][slug] = {"url": url, "pairs": [], "fetch_failed": True}
            json.dump(state, open(OUT, "w"))
            return "fail"

if __name__ == "__main__":
    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(worker, u): u for u in PAGES}
        for f in futs:
            try:
                r = f.result()
            except Exception as e:
                r = "exc %s" % e
            done += 1
            if done % 10 == 0:
                print("progress", done, "/", len(PAGES), flush=True)
    ok = sum(1 for v in state["pages"].values() if v["pairs"])
    print("DONE pages=%d ok=%d pairs=%d" % (len(state["pages"]), ok,
          sum(len(v["pairs"]) for v in state["pages"].values())))
