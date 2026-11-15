#!/usr/bin/env python3
"""team08: re-verify pending codes 142-284 from wave_20261112_pending_all.json.
Spaced, low concurrency (2 workers), one requests.Session, browser UA.
Controls first; 429/transport -> PENDING, never dead. Empty og:title -> retry 2-3x.
"""
import json, re, time, sys
from concurrent.futures import ThreadPoolExecutor
import requests
from html import unescape

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/"
PEND = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/wave_20261112_pending_all.json"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
GENERIC = {"", "whatsapp", "whatsapp group invite", "whatsapp group", "whatsapp group link",
           "join whatsapp group", "whatsapp groups"}

def og_title(html):
    m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html, re.I | re.S)
    if not m:
        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:title["\']', html, re.I | re.S)
    if not m:
        return ""
    return unescape(m.group(1)).strip()

CATMAP = {"Online Earning": "Earning"}

# hard-screen patterns on LIVE og:title (lowercased)
PORN = [r"\bxxx\b", r"\bporn\b", r"\bsex\b", r"\bsexy\b", r"18\+\s*(video|porn|sex|xxx)",
        r"\bdesi\s*(sex|porn|xxx)\b", r"\bnude\b", r"\bhot\s*girl", r"call\s*girl"]
SCAM = [r"airdrop", r"binary\s*option", r"free\s*money", r"earn\s*\$?\d+\s*(daily|per day)",
        r"double\s*(your\s*)?money", r"investment\s*double", r"click\s*.*earn"]
CASINO = [r"tigrinho", r"fortune\s*tiger", r"\bsinais\b", r"plataformas?\s*pagantes?",
          r"\bcasino\b", r"\bslots?\b", r"betting\s*signal", r"\bwjbet\b", r"\bbet\s*signal",
          r"aviator\s*signal", r"\bcrash\s*signal"]

def screen(title):
    t = title.lower()
    for pat in PORN:
        if re.search(pat, t): return "porn/xxx: " + pat
    for pat in CASINO:
        if re.search(pat, t): return "casino/betting: " + pat
    for pat in SCAM:
        if re.search(pat, t): return "scam/crypto-airdrop: " + pat
    return None

def fetch(session, code, attempts=3):
    url = "https://chat.whatsapp.com/" + code
    last_err = ""
    for a in range(attempts):
        try:
            r = session.get(url, headers=UA, timeout=75)
            if r.status_code == 429:
                return ("pending", "", "http 429 (attempt %d)" % (a + 1))
            if r.status_code != 200:
                last_err = "http %d" % r.status_code
                time.sleep(4)
                continue
            title = og_title(r.text or "")
            if title and title.lower().strip() not in GENERIC:
                return ("live", title, "")
            last_err = "empty/generic og:title"
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            last_err = "transport:%s" % type(e).__name__
            time.sleep(5)
    if "429" in last_err or "transport" in last_err:
        return ("pending", "", last_err)
    return ("dead", "", last_err)

def main():
    pending = json.load(open(PEND))
    slice_items = pending[142:285]
    assert len(slice_items) == 143, len(slice_items)
    union = set(json.load(open(UNION)))
    seen = set()
    session = requests.Session()

    # ---- CONTROLS ----
    st, title, err = fetch(session, "KrDwdK8EIkB6vgauHg5M7N")
    ctrl_live = (st == "live" and title == "JAY - PHP & Python Full Stack Developer")
    print("CONTROL live:", st, repr(title), "PASS" if ctrl_live else "FAIL", flush=True)
    st2, title2, err2 = fetch(session, "ZzZzZzZzZzZzZzZzZzZzZzZz")
    ctrl_fake = (st2 == "dead" and title2 == "")
    print("CONTROL fabricated:", st2, repr(title2), "PASS" if ctrl_fake else "FAIL", flush=True)
    if not (ctrl_live and ctrl_fake):
        print("CONTROLS FAILED — STOPPING", flush=True)
        json.dump({"team": "team08", "controls": {"live": {"status": st, "title": title, "pass": ctrl_live},
                   "fabricated": {"status": st2, "title": title2, "pass": ctrl_fake}},
                   "stopped": True}, open(WAVE + "team08-summary.json", "w"), indent=2)
        sys.exit(1)

    results = []  # (item, status, title, reason)
    BATCH = 8
    for i in range(0, len(slice_items), BATCH):
        batch = slice_items[i:i + BATCH]
        with ThreadPoolExecutor(max_workers=2) as ex:
            outs = list(ex.map(lambda it: fetch(session, it["invite"].rsplit("/", 1)[-1]), batch))
        for it, (st, title, err) in zip(batch, outs):
            code = it["invite"].rsplit("/", 1)[-1]
            results.append((it, code, st, title, err))
            print(i, code, st, repr(title)[:80], err, flush=True)
        # bank partial progress
        json.dump([{"code": c, "status": s, "title": t, "reason": e} for _, c, s, t, e in results],
                  open(WAVE + "team08-progress.json", "w"), indent=2)
        if i + BATCH < len(slice_items):
            time.sleep(6)

    candidates, leads, still_pending, excluded = [], [], [], []
    n_dup = n_dead = 0
    for it, code, st, title, err in results:
        if code in union or code in seen:
            n_dup += 1
            excluded.append({"code": code, "reason": "duplicate"})
            continue
        seen.add(code)
        if st == "pending":
            still_pending.append({"code": code, "reason": err, "name": it.get("name", ""),
                                  "invite": it["invite"]})
            continue
        if st == "dead":
            n_dead += 1
            continue
        # live
        sreason = screen(title)
        if sreason:
            excluded.append({"code": code, "reason": "excluded: " + sreason + " | title=" + title})
            continue
        cat = CATMAP.get(it.get("category", ""), it.get("category", "") or "Community & Social")
        country = it.get("country", "") or ""
        name = title
        desc = "Join %s, an active WhatsApp group for %s." % (name, cat.lower())
        if country:
            desc += " Connect with members, share updates and stay in touch."
        else:
            desc += " Connect with members, share updates and stay in touch."
        item = {"name": name, "category": cat, "country": country,
                "description": desc, "invite": "https://chat.whatsapp.com/" + code}
        candidates.append(item)
        leads.append(item)

    json.dump(candidates, open(WAVE + "team08-candidates.json", "w"), indent=2, ensure_ascii=False)
    json.dump(leads, open(WAVE + "team08-leads.json", "w"), indent=2, ensure_ascii=False)
    json.dump(still_pending, open(WAVE + "team08-pending.json", "w"), indent=2, ensure_ascii=False)
    summary = {
        "team": "team08",
        "slice": "pending codes 142-284 (0-based) of wave_20261112_pending_all.json (143 codes)",
        "sources": ["wave_20261112_pending_all.json items 142-284; _team_file team13-pending-recheck-pending.json (72) + team20-77links-pending.json (71); all prior reason HTTP 429/transport"],
        "controls": {"live_KrDwdK8EIkB6vgauHg5M7N": {"expected": "JAY - PHP & Python Full Stack Developer", "got": None, "pass": ctrl_live},
                     "fabricated_ZzZzZzZzZzZzZzZzZzZzZzZz": {"expected": "empty", "got_status": st2, "pass": ctrl_fake}},
        "counts": {"raw": 143, "verified_live": len(candidates), "dupes": n_dup,
                   "dead": n_dead, "excluded": len(excluded), "pending": len(still_pending),
                   "leads": len(leads)},
        "excluded": excluded,
        "pending_detail": still_pending,
        "resume_point": "slice fully processed (143/143); still-pending codes listed in team08-pending.json",
        "notes": "Names taken from live og:title; category/country from pending file (Online Earning mapped to canonical Earning). Descriptions generated, never copied. No source name/link stored."
    }
    # fill control got title
    summary["controls"]["live_KrDwdK8EIkB6vgauHg5M7N"]["got"] = title if ctrl_live else title
    json.dump(summary, open(WAVE + "team08-summary.json", "w"), indent=2, ensure_ascii=False)
    print("DONE", summary["counts"], flush=True)

if __name__ == "__main__":
    main()
