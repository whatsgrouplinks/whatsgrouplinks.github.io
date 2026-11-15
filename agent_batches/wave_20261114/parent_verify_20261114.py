#!/usr/bin/env python3
"""Parent verification for wave 20261114 + wave12 team02 weak-signal spot check.
LIVE = non-empty, non-generic og:title. Empty og:title -> 1 retry after 3s.
"""
import json, random, re, time, sys
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
BUILD = "/home/hatch/workspace/whatsapp-groups-site"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)

def check(sess, code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in (1, 2):
        try:
            r = sess.get(url, headers=UA, timeout=60)
            m = TITLE_RE.search(r.text or "")
            title = (m.group(1).strip() if m else "")
            if title and title != "WhatsApp Group Invite":
                return ("live", title, r.status_code)
            if attempt == 1:
                time.sleep(3)
        except Exception as e:
            if attempt == 1:
                time.sleep(3)
                continue
            return ("transport", str(e)[:80], 0)
    return ("dead", title if 'title' in dir() else "", 0)

def main():
    clean = json.load(open(f"{WAVE}/wave_20261114_clean.json"))
    rnd = random.Random(20261114)
    sample = rnd.sample(clean, 35)
    team24 = ["BzD8xwxi9Dl5kpfqNSiB4C","FSVxZQDm2Jz9fmzKndgbvi","LXlFviZyzYt5y3XEcLNmHm",
              "G6UvTNAjewrIFpC7BR76kn","GRcsQrFQBxS0Ka5wbzzwCo","EpdfRt8EfuUDMxp9RiAZwz","JQe8xWPbf5P8D6cr15Jee6"]
    st12 = json.load(open(f"{BUILD}/agent_batches/wave_20261112/team02-verify-state.json"))
    weak = [c for c, v in st12.items() if v.get("status") == "live" and not v.get("og")]
    print("wave12 team02 weak-signal 'live' codes:", len(weak), "of", len(st12))
    w12sample = weak  # only 12 codes lack an og title (coordinator's "many" was a misread)
    sess = requests.Session()
    out = {"controls": {}, "clean_sample": [], "team24": [], "wave12_weak": []}
    # controls first
    for label, code in [("live_control", "KrDwdK8EIkB6vgauHg5M7N"), ("fab_control", "ZZZZQQQQXXXXWWWWVVVV")]:
        res = check(sess, code)
        out["controls"][label] = {"code": code, "verdict": res[0], "title": res[1]}
        print("CONTROL", label, res)
        time.sleep(1.5)
    for group, items in [("clean_sample", [(c["invite"].rsplit("/", 1)[-1], c["name"]) for c in sample]),
                         ("team24", [(c, "") for c in team24]),
                         ("wave12_weak", [(c, "") for c in w12sample])]:
        for code, name in items:
            res = check(sess, code)
            out[group].append({"code": code, "name": name, "verdict": res[0], "title": res[1]})
            print(group, code, res[0], "|", (res[1] or "")[:60], "|", name[:40])
            time.sleep(1.5)
    json.dump(out, open(f"{WAVE}/parent_verify_20261114.json", "w"), ensure_ascii=False, indent=1)
    for g in ("clean_sample", "team24", "wave12_weak"):
        from collections import Counter
        print(g, Counter(x["verdict"] for x in out[g]))

if __name__ == "__main__":
    main()
