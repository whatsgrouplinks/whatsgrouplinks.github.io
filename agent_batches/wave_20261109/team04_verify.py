import json, re, subprocess, os, time, html, threading
from concurrent.futures import ThreadPoolExecutor

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CKPT = os.path.join(W, "team04_verify_ckpt.jsonl")

OG_RE = re.compile(r'og:title["\']\s+content=["\']([^"\']*)["\']', re.I)
OG_RE2 = re.compile(r'content=["\']([^"\']*)["\']\s+property=["\']og:title["\']', re.I)

def check_once(code):
    try:
        r = subprocess.run(
            ["curl","-sL","--max-time","20","-A",UA,
             "-o",f"/tmp/team04_wa_{code}.html","-w","%{http_code}",
             f"https://chat.whatsapp.com/{code}"],
            capture_output=True, text=True, timeout=35)
        http = (r.stdout or "").strip()
        if r.returncode != 0 or not http or http == "000":
            return None, None  # transport fail
        body = open(f"/tmp/team04_wa_{code}.html", encoding="utf-8", errors="ignore").read()
        m = OG_RE.search(body) or OG_RE2.search(body)
        title = html.unescape(m.group(1)).strip() if m else ""
        # WhatsApp default placeholder titles are not real group names
        return int(http), title
    except Exception:
        return None, None

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

def work(code):
    if code in done:
        return
    g = to_verify[code]
    attempts = []
    status = None; title = ""
    for attempt in range(3):
        http, t = check_once(code)
        attempts.append({"http": http, "title": t})
        if http is None:
            status = "transport-fail"; break
        if http == 200 and t:
            status = "live"; title = t; break
        if http == 200 and not t:
            if attempt < 2:
                time.sleep(5)  # spaced-apart retry for ambiguous
                continue
            status = "dead-empty-title"; break
        # non-200 (404 etc.)
        status = "dead-http"; title = t or ""; break
        time.sleep(0.6)
    rec = {"code": code, "status": status, "og_title": title, "attempts": attempts,
           "from_url": g.get("from_url"), "from_source": g.get("from_source")}
    with lock:
        with open(CKPT, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        done[code] = rec
    print(f"{code} {status} http={attempts[-1]['http']} title={title[:40]!r}", flush=True)
    time.sleep(0.6)

codes = [c for c in to_verify if c not in done]
print(f"todo: {len(codes)}", flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, codes))
print("VERIFY DONE", flush=True)
