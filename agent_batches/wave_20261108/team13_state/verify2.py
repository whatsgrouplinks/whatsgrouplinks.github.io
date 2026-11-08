"""Team 13 verifier v2: live-check chat.whatsapp.com/<code> via curl subprocess
(hard --max-time wall clock; requests/urllib3 read-timeout can hang on trickle).
Rules: max 3 parallel, >=0.7s between check starts. Live = 200 + non-empty og:title
not generic. Empty og:title on 200 -> retry once after pause, then dead.
Transport error/timeout -> retry once -> pending (reason transport).
429 -> retry once -> pending. Usage: verify2.py <candidates.json> <live.json> <pending.json>
Resumable; saves incrementally.
"""
import re, time, json, os, sys, threading, html as ihtml, subprocess
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
GENERIC = {"whatsapp group", "join this group on whatsapp", "whatsapp group invite"}
TITLE_RE = re.compile(r'<meta[^>]+property="og:title"[^>]*>', re.I)
DESC_RE = re.compile(r'<meta[^>]+property="og:description"[^>]*>', re.I)
CONTENT_RE = re.compile(r'content="([^"]*)"')

pace_lock = threading.Lock()
last_start = [0.0]

def paced():
    with pace_lock:
        now = time.time()
        wait = 0.7 - (now - last_start[0])
        if wait > 0:
            time.sleep(wait)
        last_start[0] = time.time()

def og_meta(text, rx):
    m = rx.search(text)
    if not m:
        return ""
    c = CONTENT_RE.search(m.group(0))
    return ihtml.unescape(c.group(1)).strip() if c else ""

def fetch_once(code):
    """Returns (status, text) or raises on transport failure. Hard 25s wall clock."""
    p = subprocess.run(
        ["curl", "-s", "-o", "/dev/stdout", "-w", "\n%{http_code}",
         "--max-time", "25", "-A", UA,
         "https://chat.whatsapp.com/" + code],
        capture_output=True, text=True, timeout=35)
    out = p.stdout
    if p.returncode != 0 or not out:
        raise RuntimeError("curl rc=%d" % p.returncode)
    lines = out.rsplit("\n", 1)
    if len(lines) < 2:
        raise RuntimeError("curl bad output")
    try:
        st = int(lines[1].strip())
    except ValueError:
        raise RuntimeError("curl bad status")
    return st, lines[0]

def check(code):
    paced()
    try:
        st, text = fetch_once(code)
    except Exception:
        time.sleep(4)
        paced()
        try:
            st, text = fetch_once(code)
        except Exception:
            return ("pending-transport", "", "")
    if st == 429:
        time.sleep(8)
        paced()
        try:
            st, text = fetch_once(code)
        except Exception:
            return ("pending-transport", "", "")
        if st == 429:
            return ("pending-rate", "", "")
    if st != 200:
        return ("dead", "", "")
    title = og_meta(text, TITLE_RE)
    desc = og_meta(text, DESC_RE)
    if title and title.lower() not in GENERIC:
        return ("live", title, desc)
    if not title:
        time.sleep(4)
        paced()
        try:
            st2, text2 = fetch_once(code)
        except Exception:
            return ("pending-transport", "", "")
        if st2 == 429:
            return ("pending-rate", "", "")
        if st2 != 200:
            return ("dead", "", "")
        title = og_meta(text2, TITLE_RE)
        desc = og_meta(text2, DESC_RE)
        if title and title.lower() not in GENERIC:
            return ("live", title, desc)
        return ("dead", "", desc)
    return ("dead", "", desc)

def main():
    cand_path, live_path, pend_path = sys.argv[1], sys.argv[2], sys.argv[3]
    cands = json.load(open(cand_path))
    live, pend = [], []
    done = set()
    for p in (live_path, pend_path):
        if os.path.exists(p):
            for it in json.load(open(p)):
                done.add(it["code"])
                (live if p == live_path else pend).append(it)
    todo = [c for c in cands if c["code"] not in done]
    print("candidates %d already done %d to check %d" % (len(cands), len(done), len(todo)), flush=True)
    lock = threading.Lock()
    counts = {"live": len(live), "dead": 0, "pending": len(pend)}

    def work(it):
        st, title, desc = check(it["code"])
        with lock:
            if st == "live":
                live.append({"name": it["name"], "code": it["code"], "og_title": title,
                             "og_desc": desc, "slug": it.get("slug", ""), "source": it.get("source", ""),
                             "category_slug": it.get("category_slug", ""), "country_slug": it.get("country_slug", ""),
                             "description": it.get("description", "")})
                counts["live"] += 1
            elif st.startswith("pending"):
                pend.append({"name": it["name"], "code": it["code"], "slug": it.get("slug", ""),
                             "source": it.get("source", ""), "note": st})
                counts["pending"] += 1
            else:
                counts["dead"] += 1
            n = counts["live"] + counts["dead"] + counts["pending"]
            if n % 25 == 0:
                json.dump(live, open(live_path, "w"), ensure_ascii=False)
                json.dump(pend, open(pend_path, "w"), ensure_ascii=False)
                print("progress live=%d dead=%d pending=%d" % (counts["live"], counts["dead"], counts["pending"]), flush=True)
        return st

    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, todo))
    json.dump(live, open(live_path, "w"), ensure_ascii=False)
    json.dump(pend, open(pend_path, "w"), ensure_ascii=False)
    print("DONE live=%d dead=%d pending=%d" % (counts["live"], counts["dead"], counts["pending"]), flush=True)

if __name__ == "__main__":
    main()
