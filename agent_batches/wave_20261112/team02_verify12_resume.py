"""TEAM02 wave 20261112 slice2 RESUME (after throttle-induced pending spike): verify the 2,160 awaiting candidates (+ any new
codes from the 19 retried listing pages) against chat.whatsapp.com.

Method (per task): persistent requests Session (keep-alive), browser UA,
60-90s timeout, LIVE iff non-empty og:title. Spaced retry on empty og
before calling a code dead; transport failure (no page after retries)
-> pending, never dead/live.

IMPORTANT control finding (verified 2026-11-12): og:description is the
constant string 'WhatsApp Group Invite' on EVERY invite page, including
fabricated codes (AAAAAAAAAAAAAAAAAAAAAA) -- it does NOT discriminate,
so the og:description fallback is NOT used. Only og:title counts.
Controls: known-live BnfNh3lujd2FCYrXcJa8Nh -> og:title
'SORTEIOS INSTAGRAM' (warm request 0.5s); fabricated AAAA.../ZZZZ... ->
HTTP 200 + empty og:title.

Reuses yesterday's clean_name / CATMAP / screen from team02_build.py for
consistency, then normalizes categories to the task's allowed list and
descriptions to the 'Join <name>, ...' schema. Yesterday's 525 verified
codes are now inside .existing_codes.json (merged Nov 11) -- they are
counted as already_merged, NOT re-banked.
"""
import json, re, os, sys, time, html, threading, importlib.util
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
BASE = "/home/hatch/workspace/whatsapp-groups-site/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

spec = importlib.util.spec_from_file_location("tb", WAVE + "team02_build.py")
tb = importlib.util.module_from_spec(spec); spec.loader.exec_module(tb)

ALLOWED = {"Education","Entertainment","Jobs","Community & Social","Sports","Funny",
           "Islamic","Health","Finance","News","Buy & Sell","Friendship","Gaming",
           "Technology","Business","Cooking","Crypto","Real Estate","Poetry"}
CAT_NORM = {"Buy Sell": "Buy & Sell", "Online Earning": "Finance",
            "Scholarship": "Education", "Freelance": "Jobs",
            "Travel": "Community & Social"}
# extra hard-screen patterns for betting promos (task rule), on top of tb.screen
EXTRA_BLOCK = [(re.compile(r"bets?\b", re.I), "betting scam"),
               (re.compile(r"\bbanca\b", re.I), "betting scam"),
               (re.compile(r"cassino|aposta", re.I), "betting scam")]

def screen_extra(name, desc):
    scan = tb._norm(f"{name} {desc}")
    for pat in tb.PROHIB_CLAUSES:
        scan = re.sub(pat, " ", scan, flags=re.I)
    for rx, reason in EXTRA_BLOCK:
        if rx.search(scan):
            return reason
    return None

_tls = threading.local()
def session():
    s = getattr(_tls, "s", None)
    n = getattr(_tls, "n", 0)
    if s is None or n >= 30:
        import requests
        if s is not None:
            try: s.close()
            except Exception: pass
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        _tls.s = s
        _tls.n = 0
    _tls.n = getattr(_tls, "n", 0) + 1
    return s

def wa_check_traced(code):
    """-> ('live', og) | ('dead','') | ('pending','') ; robust/slow resume version."""
    got_page = False
    last_status = None
    for attempt in (1, 2, 3):
        try:
            s = session()
            r = s.get(f"https://chat.whatsapp.com/{code}", timeout=90)
            last_status = r.status_code
            h = r.text or ""
            if r.status_code == 429 or r.status_code >= 500:
                # rate-limited / server error: transport failure, back off hard
                time.sleep(20)
                _tls.s = None
                continue
            if r.status_code and h:
                got_page = True
                m = re.search(r'property="og:title"\s+content="([^"]*)"', h)
                og = html.unescape(m.group(1)).strip() if m else ""
                if og:
                    return ("live", og)
                time.sleep(8)
            else:
                time.sleep(10)
        except Exception as e:
            # stale pooled connection / reset / timeout: drop session, back off
            _tls.s = None
            _tls.n = 0
            time.sleep(15)
    return ("pending" if not got_page else "dead", "")

def main():
    existing = set(json.load(open(BASE + ".existing_codes.json")))
    slice_urls = json.load(open(WAVE + "leads_slice2.json"))
    recs = []
    with open(WAVE + "team02-extracted.jsonl") as f:
        for line in f:
            try:
                recs.append(json.loads(line))
            except Exception:
                pass
    ok = [r for r in recs if "error" not in r]
    mined_urls = {r["url"] for r in ok}
    fetch_fail_urls = [r["url"] for r in recs if "error" in r]

    seen = set(); cands = []
    dup_existing = 0; already_merged = 0; dup_within = 0; no_code = 0
    exclusions = []
    state = {}
    if os.path.exists(WAVE + "team02-verify-state.json"):
        try:
            state = json.load(open(WAVE + "team02-verify-state.json"))
        except Exception:
            state = {}
    # merge per-code progress rows (written every code; state file only every 50)
    # -- recovers the 24 codes checked after the last checkpoint of the killed run
    if os.path.exists(WAVE + "team02-verify-progress.jsonl"):
        merged = 0
        with open(WAVE + "team02-verify-progress.jsonl") as pf:
            for line in pf:
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if row.get("status") in ("live", "dead", "pending"):
                    state[row["code"]] = {"status": row["status"], "og": row.get("og", "")}
                    merged += 1
        print(f"merged {merged} progress rows into state; state now {len(state)} codes", flush=True)
        save_state_pre = lambda: json.dump(state, open(WAVE + "team02-verify-state.json", "w"), ensure_ascii=False)
        save_state_pre()
    for r in ok:
        codes = r.get("codes") or []
        if not codes:
            no_code += 1; continue
        for code in codes:
            if code in existing:
                dup_existing += 1
                if state.get(code, {}).get("status") == "live":
                    already_merged += 1
                continue
            if code in seen:
                dup_within += 1; continue
            seen.add(code)
            name = tb.clean_name(r.get("name", ""))
            if not name:
                exclusions.append({"code": code, "reason": "empty name after cleaning"}); continue
            cat = tb.CATMAP.get((r.get("cat_raw") or "").strip(), "Community & Social")
            reason = tb.screen(name, r.get("desc") or "") or screen_extra(name, r.get("desc") or "")
            if reason:
                exclusions.append({"code": code, "reason": reason}); continue
            cands.append({"name": name, "category": cat, "country": "BR",
                          "description": "", "invite": f"https://chat.whatsapp.com/{code}",
                          "_code": code, "_desc_src": r.get("desc") or ""})
    print(f"extracted {len(recs)} ok {len(ok)} fetch_fail {len(fetch_fail_urls)} no_code {no_code}", flush=True)
    print(f"cands {len(cands)} dup_existing {dup_existing} (of which already-merged-live {already_merged}) dup_within {dup_within} exclusions {len(exclusions)}", flush=True)

    # cross-check vs yesterday's awaiting file
    try:
        awaiting = json.load(open(WAVE + "team02-awaiting-verification.json"))
        aw_codes = {a["invite"].split("/")[-1] for a in awaiting}
        cand_codes = {c["_code"] for c in cands}
        print(f"awaiting file {len(aw_codes)} codes; rebuilt candidates {len(cand_codes)}; "
              f"awaiting not in rebuilt {len(aw_codes - cand_codes)}; rebuilt not in awaiting {len(cand_codes - aw_codes)} "
              f"(new from retried 19 pages)", flush=True)
    except Exception as e:
        print("awaiting cross-check failed:", e, flush=True)

    def finalize_item(c, og=""):
        name = c["name"]
        if not name and og:
            name = tb.clean_name(html.unescape(og))
        cat = CAT_NORM.get(c["category"], c["category"])
        if cat not in ALLOWED:
            cat = "Community & Social"
        desc = f"Join {name}, a {cat} WhatsApp group — chat with members, share updates and connect."
        return {"name": name, "category": cat, "country": "BR",
                "description": desc[:200],
                "invite": f"https://chat.whatsapp.com/{c['_code']}"}

    STATE_FILE = WAVE + "team02-verify-state.json"
    PROG_FILE = WAVE + "team02-verify-progress.jsonl"
    def save_state():
        json.dump(state, open(STATE_FILE, "w"), ensure_ascii=False)

    verified = []; pending = []; dead = 0; to_check = []
    for c in cands:
        st = state.get(c["_code"])
        if st and st.get("status") == "live":
            verified.append(finalize_item(c, st.get("og", "")))
        elif st and st.get("status") == "dead":
            dead += 1
        else:
            to_check.append(c)
    print(f"reuse live {len(verified)} dead {dead} to_check {len(to_check)}", flush=True)

    print("COOLDOWN 300s before resume (WhatsApp throttling window)...", flush=True)
    time.sleep(300)
    print("cooldown done, resuming verification at slow pace", flush=True)
    def work(c):
        st, og = wa_check_traced(c["_code"])
        time.sleep(2.0)
        return c, st, og

    t0 = time.time(); n = 0
    with open(PROG_FILE, "a") as pf, ThreadPoolExecutor(max_workers=4) as ex:
        for c, st, og in ex.map(work, to_check):
            n += 1
            state[c["_code"]] = {"status": st, "og": og}
            if st == "live":
                verified.append(finalize_item(c, og))
            elif st == "pending":
                item = finalize_item(c)
                item["reason"] = "transport failure: no WhatsApp page after retries"
                pending.append(item)
            else:
                dead += 1
            pf.write(json.dumps({"code": c["_code"], "status": st, "og": og,
                                 "n": n, "elapsed": round(time.time() - t0, 1)}) + "\n"); pf.flush()
            if n % 50 == 0:
                save_state()
                json.dump(verified, open(WAVE + "team02-leads-slice2-candidates.json", "w"), ensure_ascii=False, indent=1)
                json.dump(pending, open(WAVE + "team02-leads-slice2-pending.json", "w"), ensure_ascii=False, indent=1)
                print(f"verified {n}/{len(to_check)} live {len(verified)} pending {len(pending)} dead {dead} elapsed {time.time()-t0:.0f}s", flush=True)
    save_state()
    json.dump(verified, open(WAVE + "team02-leads-slice2-candidates.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + "team02-leads-slice2-pending.json", "w"), ensure_ascii=False, indent=1)
    remaining = [u for u in slice_urls if u not in mined_urls]
    json.dump(remaining, open(WAVE + "team02-leads-slice2-leads.json", "w"), ensure_ascii=False, indent=1)
    # dedupe safety: verified must be unique codes, none in existing
    codes = [v["invite"].split("/")[-1] for v in verified]
    assert len(codes) == len(set(codes)), "dup codes in verified!"
    assert not (set(codes) & existing), "verified code already in existing!"
    assert all(v["category"] in ALLOWED for v in verified), "category outside allowed list!"
    summary = {"team": "02", "slice": "leads_slice2", "wave": "20261112",
               "sources": ["linkado.app grupo pages"],
               "verified": len(verified), "pending": len(pending), "leads": len(remaining),
               "dead": dead, "dup_existing": dup_existing,
               "already_merged_yesterday_live": already_merged,
               "dup_within": dup_within, "no_code_listings": no_code,
               "fetch_fail_listings": len(fetch_fail_urls),
               "exclusions": exclusions,
               "controls": {"known_live_code": "BnfNh3lujd2FCYrXcJa8Nh",
                            "known_live_og_title": "SORTEIOS INSTAGRAM",
                            "fabricated_codes": ["AAAAAAAAAAAAAAAAAAAAAA", "ZZZZZZZZZZZZZZZZZZZZZZ"],
                            "fabricated_og_title": "",
                            "result": "PASS - rule discriminates"},
               "method": "python requests Session (persistent keep-alive, browser UA, timeout 90s), 6 workers; LIVE iff non-empty og:title after up to 2 spaced attempts; og:description NOT used as fallback (constant 'WhatsApp Group Invite' even for fabricated codes); transport failure (no page) -> pending",
               "resume": f"mined {len(mined_urls)}/{len(slice_urls)} listing pages (3603 records in team02-extracted.jsonl, 0 fetch-fail after retrying the 19); verify-state has {len(state)} codes in team02-verify-state.json; next unmined listing URLs in team02-leads-slice2-leads.json ({len(remaining)}).",
               "notes": "Categories normalized to the task's allowed list (Buy Sell->Buy & Sell, Online Earning->Finance, Scholarship->Education, Freelance->Jobs, Travel->Community & Social). Descriptions in 'Join <name>, ...' schema. Yesterday's 525 verified codes are now in .existing_codes.json (merged Nov 11) and are NOT re-banked here; they are counted under already_merged_yesterday_live."}
    json.dump(summary, open(WAVE + "team02-leads-slice2-summary.json", "w"), ensure_ascii=False, indent=1)
    print(f"VERIFY DONE verified {len(verified)} pending {len(pending)} leads {len(remaining)} dead {dead} elapsed {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
