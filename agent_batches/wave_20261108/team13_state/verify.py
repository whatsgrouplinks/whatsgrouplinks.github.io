"""Team 13 verifier: live-check chat.whatsapp.com/<code> for candidate codes.
Rules: max 3 parallel, >=0.7s between check starts. Live = 200 + non-empty og:title
not generic. Empty og:title on 200 -> retry once after pause w/ fresh session, then dead.
Transport error -> retry once -> pending (reason transport). 429 -> retry once -> pending.
Usage: verify.py <candidates.json> <out_live.json> <out_pending.json>
Saves incrementally; resumable (skips codes already in out files).
"""
import requests, re, time, json, os, sys, threading, html as ihtml
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

_tls = threading.local()

def get_session():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA,
                          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                          "Accept-Language": "en-US,en;q=0.9"})
        _tls.s = s
    return s

def fresh_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA,
                      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                      "Accept-Language": "en-US,en;q=0.9"})
    return s

def og_meta(text, rx):
    m = rx.search(text)
    if not m:
        return ""
    c = CONTENT_RE.search(m.group(0))
    return ihtml.unescape(c.group(1)).strip() if c else ""

def fetch_once(code, fresh=False):
    s = fresh_session() if fresh else get_session()
    r = s.get("https://chat.whatsapp.com/" + code, timeout=(8, 12))
    return r.status_code, r.text

def check(code):
    """Returns (status, title, desc): status in live/dead/pending-transport/pending-rate."""
    paced()
    try:
        st, text = fetch_once(code)
    except Exception:
        time.sleep(5)
        paced()
        try:
            st, text = fetch_once(code)
        except Exception:
            return ("pending-transport", "", "")
    if st == 429:
        time.sleep(10)
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
        # ambiguous: retry once after pause with fresh session
        time.sleep(6)
        paced()
        try:
            st2, text2 = fetch_once(code, fresh=True)
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
    return ("dead", "", desc)  # generic title

def main():
    cand_path, live_path, pend_path = sys.argv[1], sys.argv[2], sys.argv[3]
    dead_path = live_path.replace("live_", "dead_")
    cands = json.load(open(cand_path))
    live, pend, dead_list = [], [], []
    done = set()
    for p in (live_path, pend_path, dead_path):
        if os.path.exists(p):
            for it in json.load(open(p)):
                done.add(it["code"])
                if p == live_path:
                    live.append(it)
                elif p == pend_path:
                    pend.append(it)
                else:
                    dead_list.append(it)
    todo = [c for c in cands if c["code"] not in done]
    print("candidates %d already done %d to check %d" % (len(cands), len(done), len(todo)), flush=True)
    lock = threading.Lock()
    counts = {"live": len(live), "dead": len(dead_list), "pending": len(pend)}

    def save_all():
        json.dump(live, open(live_path, "w"), ensure_ascii=False)
        json.dump(pend, open(pend_path, "w"), ensure_ascii=False)
        json.dump(dead_list, open(dead_path, "w"), ensure_ascii=False)

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
                dead_list.append({"name": it["name"], "code": it["code"], "slug": it.get("slug", ""),
                                  "source": it.get("source", "")})
                counts["dead"] += 1
            if (counts["live"] + counts["dead"] + counts["pending"]) % 25 == 0:
                save_all()
                print("progress live=%d dead=%d pending=%d" % (counts["live"], counts["dead"], counts["pending"]), flush=True)
        return st

    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, todo))
    save_all()
    print("DONE live=%d dead=%d pending=%d" % (counts["live"], counts["dead"], counts["pending"]), flush=True)

if __name__ == "__main__":
    main()
