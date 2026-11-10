import json, re, subprocess, os, html, time, threading
from concurrent.futures import ThreadPoolExecutor

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CKPT = os.path.join(W, "team04_verify_ckpt.jsonl")
OG_RE = re.compile(r'og:title["\']\s+content=["\']([^"\']*)["\']', re.I)
OG_RE2 = re.compile(r'content=["\']([^"\']*)["\']\s+property=["\']og:title["\']', re.I)
OGD_RE = re.compile(r'og:description["\']\s+content=["\']([^"\']*)["\']', re.I)

def check_once(code):
    p = f"/tmp/team04v10_{code}.html"
    try:
        r = subprocess.run(
            ["curl","-sL","--max-time","15","-A",UA,"-o",p,"-w","%{http_code}",
             f"https://chat.whatsapp.com/{code}"],
            capture_output=True, text=True, timeout=25)
        http = (r.stdout or "").strip()
        if r.returncode != 0 or not http or http == "000":
            return None, None, None
        body = open(p, encoding="utf-8", errors="ignore").read()
        m = OG_RE.search(body) or OG_RE2.search(body)
        title = html.unescape(m.group(1)).strip() if m else ""
        md = OGD_RE.search(body)
        desc = html.unescape(md.group(1)).strip() if md else ""
        try: os.remove(p)
        except Exception: pass
        return int(http), title, desc
    except Exception:
        return None, None, None

to_verify = json.load(open(os.path.join(W, "team04_to_verify.json")))
done = {}
if os.path.exists(CKPT):
    with open(CKPT) as f:
        for line in f:
            try:
                rec = json.loads(line); done[rec["code"]] = rec
            except Exception: pass
print(f"resuming: {len(done)} already checked of {len(to_verify)}", flush=True)
lock = threading.Lock()
GENERIC = {"whatsapp", "whatsapp group invite", "join group", "join group on whatsapp", "invite", "group invite"}

def work(code):
    if code in done:
        return
    status = None; title = ""; desc = ""; http_last = None
    for attempt in range(3):
        http, t, d = check_once(code)
        http_last = http
        if http is None:
            status = "transport-fail"; break
        if http == 200 and t and t.lower() not in GENERIC:
            status = "live"; title = t; desc = d or ""; break
        if http == 200 and (not t or t.lower() in GENERIC):
            status = "dead-empty-title"; title = t or ""
            if attempt < 2:
                time.sleep(2)
                continue
            break
        status = "dead-http"; title = t or ""
        break
    rec = {"code": code, "status": status, "http": http_last, "title": title, "desc": desc}
    with lock:
        with open(CKPT, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        done[code] = rec
    print(f"{code} {status} http={http_last} title={title[:50]!r}", flush=True)

codes = list(to_verify.keys())
# stagger workers: each worker sleeps 0.6s between its own checks
def worker(chunk):
    for code in chunk:
        work(code)
        time.sleep(0.6)

chunks = [codes[i::3] for i in range(3)]
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(worker, chunks))
print("VERIFY DONE", flush=True)
