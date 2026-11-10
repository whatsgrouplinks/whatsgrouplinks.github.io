import json, re, os, sys, time, threading, argparse
import requests
from concurrent.futures import ThreadPoolExecutor

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CKPT = os.path.join(W, "team04_verify_ckpt.jsonl")
OG_RE = re.compile(r'og:title["\']\s+content=["\']([^"\']*)["\']', re.I)
OG_RE2 = re.compile(r'content=["\']([^"\']*)["\']\s+property=["\']og:title["\']', re.I)
OGD_RE = re.compile(r'og:description["\']\s+content=["\']([^"\']*)["\']', re.I)
GENERIC = {"whatsapp", "whatsapp group invite", "join group", "join group on whatsapp", "invite", "group invite"}

ap = argparse.ArgumentParser()
ap.add_argument("--limit", type=int, default=0)
args = ap.parse_args()

to_verify = json.load(open(os.path.join(W, "team04_to_verify.json")))
done = {}
if os.path.exists(CKPT):
    with open(CKPT) as f:
        for line in f:
            try:
                rec = json.loads(line); done[rec["code"]] = rec
            except Exception: pass
remaining = [c for c in to_verify if c not in done]
if args.limit:
    remaining = remaining[:args.limit]
print(f"checked={len(done)} remaining={len(to_verify)-len(done)} this_batch={len(remaining)}", flush=True)
lock = threading.Lock()
tls = threading.local()

def session():
    if not hasattr(tls, "s"):
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        tls.s = s
    return tls.s

def check_once(code):
    try:
        r = session().get(f"https://chat.whatsapp.com/{code}", timeout=15, stream=True)
        http = r.status_code
        head = b""
        try:
            for chunk in r.iter_content(chunk_size=8192):
                head += chunk
                if len(head) >= 40000:
                    break
        finally:
            r.close()
        text = head.decode("utf-8", errors="ignore")
        import html as _html
        m = OG_RE.search(text) or OG_RE2.search(text)
        title = _html.unescape(m.group(1)).strip() if m else ""
        md = OGD_RE.search(text)
        desc = _html.unescape(md.group(1)).strip() if md else ""
        return http, title, desc
    except Exception:
        return None, None, None

def warmup():
    # first request on a fresh proxy tunnel is very slow (~15s); absorb it once per worker
    try:
        session().get("https://chat.whatsapp.com/", timeout=25, stream=True).close()
    except Exception:
        try:
            tls.s = None
        except Exception:
            pass

def work(code):
    status = None; title = ""; desc = ""; http_last = None
    tf_retries = 0
    for attempt in range(3):
        http, t, d = check_once(code)
        http_last = http
        if http is None:
            if tf_retries < 1:
                # fresh session + one retry: first-tunnel slowness can fake a transport fail
                tf_retries += 1
                try:
                    tls.s = None
                except Exception:
                    pass
                warmup()
                time.sleep(1)
                continue
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

def worker(chunk):
    warmup()
    for code in chunk:
        t0 = time.time()
        work(code)
        el = time.time() - t0
        if el < 0.6:
            time.sleep(0.6 - el)

chunks = [remaining[i::3] for i in range(3)]
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(worker, chunks))
print("BATCH DONE", flush=True)
