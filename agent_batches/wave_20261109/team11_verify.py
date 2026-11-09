#!/usr/bin/env python3
"""Team 11 verifier: live-check chat.whatsapp.com/<code> with CURL ONLY
(python requests stalls on chat.whatsapp.com).
Rules: max 3 parallel, >=0.7s between check starts. Live = 200 + non-empty
og:title (not generic). Empty og:title on 200 -> retry up to 2 more times
spaced apart, then dead. Transport error / 429 -> retry once -> pending.
Usage: team11_verify.py <candidates.json>
Writes team11_live.json / team11_pending.json / team11_dead.json (resumable)."""
import json, os, re, subprocess, sys, threading, time, html as ihtml
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
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
    """Returns (http_code or None on transport error, text)."""
    tmp = "/tmp/team11_verify_%s_%s.html" % (code, threading.current_thread().name.replace(" ", "_"))
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "20", "-A", UA,
                            "-o", tmp, "-w", "%{http_code}",
                            "https://chat.whatsapp.com/" + code],
                           capture_output=True, text=True, timeout=30)
        http_code = int((r.stdout or "0").strip() or 0)
        text = open(tmp, encoding="utf-8", errors="ignore").read() if os.path.exists(tmp) else ""
        return http_code, text
    except Exception:
        return None, ""

def check(code):
    """Returns (status, title, desc): live/dead/pending-transport/pending-rate."""
    paced()
    st, text = fetch_once(code)
    if st is None:
        time.sleep(5)
        paced()
        st, text = fetch_once(code)
        if st is None:
            return ("pending-transport", "", "")
    if st == 429:
        time.sleep(10)
        paced()
        st, text = fetch_once(code)
        if st is None:
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
        # ambiguous: retry up to 2 more times spaced apart
        for _ in range(2):
            time.sleep(6)
            paced()
            st2, text2 = fetch_once(code)
            if st2 is None:
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
    cand_path = sys.argv[1]
    live_path = os.path.join(WAVE, "team11_live.json")
    pend_path = os.path.join(WAVE, "team11_pending_raw.json")
    dead_path = os.path.join(WAVE, "team11_dead.json")
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
            base = {"name": it["name"], "code": it["code"], "slug": it.get("slug", ""),
                    "source": it.get("source", ""), "category_slug": it.get("category_slug", ""),
                    "country_slug": it.get("country_slug", ""), "description": it.get("description", "")}
            if st == "live":
                base.update({"og_title": title, "og_desc": desc})
                live.append(base)
                counts["live"] += 1
            elif st.startswith("pending"):
                base.update({"note": st})
                pend.append(base)
                counts["pending"] += 1
            else:
                dead_list.append(base)
                counts["dead"] += 1
            total = counts["live"] + counts["dead"] + counts["pending"]
            if total % 25 == 0:
                save_all()
                print("progress live=%d dead=%d pending=%d" % (counts["live"], counts["dead"], counts["pending"]), flush=True)
        return st

    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, todo))
    save_all()
    print("DONE live=%d dead=%d pending=%d" % (counts["live"], counts["dead"], counts["pending"]), flush=True)

if __name__ == "__main__":
    main()
