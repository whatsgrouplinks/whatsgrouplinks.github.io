import json, re, subprocess, time, urllib.parse, os, threading
from concurrent.futures import ThreadPoolExecutor

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})")
CKPT = os.path.join(W, "team04_fetch_ckpt.jsonl")
LOG = os.path.join(W, "team04_fetch.log")

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")

def fetch(url):
    try:
        r = subprocess.run(["curl","-sL","--max-time","20","-A",UA,url],
                           capture_output=True, text=True, timeout=30)
        return r.stdout or ""
    except Exception:
        return ""

def norm(code):
    return code.split("?")[0].split("#")[0].rstrip("/")

leads = json.load(open(os.path.join(W, "leads_slice_04.json")))
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))

done = set()
if os.path.exists(CKPT):
    with open(CKPT) as f:
        for line in f:
            try: done.add(json.loads(line)["idx"])
            except Exception: pass
log(f"resuming: {len(done)} already done of {len(leads)}")

lock = threading.Lock()
def work(item):
    i, l = item
    if i in done:
        return
    url = l["url"]; src = l.get("source","")
    body = fetch(url)
    rec = {"idx": i, "url": url, "source": src, "len": len(body), "codes": [], "dead": None}
    if not body or len(body) < 200:
        rec["dead"] = "empty/short fetch"
    else:
        codes = sorted(set(norm(c) for c in CODE_RE.findall(body)))
        rec["codes"] = codes
        if not codes:
            rec["dead"] = "no invite codes on page"
    with lock:
        with open(CKPT, "a") as f:
            f.write(json.dumps(rec) + "\n")
        done.add(i)
    log(f"{i} len={len(body)} codes={len(rec['codes'])} {url[:80]}")

todo = [(i,l) for i,l in enumerate(leads) if i not in done]
log(f"todo: {len(todo)}")
with ThreadPoolExecutor(max_workers=5) as ex:
    list(ex.map(work, todo))
log("FETCH DONE")
