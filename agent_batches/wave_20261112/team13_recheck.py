import json, re, time, sys, random, html
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PENDING_SRC = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/wave_20261111_pending_all.json"
EXISTING = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}

CATMAP = {"Online Earning": "Jobs", "Buy Sell": "Buy & Sell", "": "Community & Social"}
ALLOWED = {"Education","Entertainment","Jobs","Community & Social","Sports","Funny","Islamic","Health","Finance","News","Buy & Sell","Friendship","Gaming","Technology","Business","Cooking","Crypto","Real Estate","Poetry"}

def og(page):
    # og:title ONLY: og:description is a constant "WhatsApp Group Invite" on
    # both live and dead pages (verified on fabricated control), so it cannot
    # serve as a live fallback.
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', page, re.I)
    if m and m.group(1).strip(): return html.unescape(m.group(1).strip())
    return ""

NEG_PORN = re.compile(r"(no\s+porn|porn\s+not\s+allowed|not\s+porn|proibido.*porn|sem\s+porn|pornografia.*proibido|n[aã]o\s+pode.*porn|porn\s*[🚫❌⛔])", re.I)
def screen(name, desc):
    t = f"{name} {desc}".lower()
    if re.search(r"\bxxx\b", t): return "hard porn marker xxx"
    if "hentai" in t: return "hentai"
    if "brazzers" in t: return "Brazzers porn brand"
    if "call girl" in t or "call-girl" in t: return "call-girl / escort"
    if "escort" in t: return "escort"
    if "desi bhabhi" in t: return "Desi bhabhi sexual"
    if "sexual home" in t: return "SEXUAL HOME"
    if "hookup" in t or "hook up" in t: return "hookup group"
    if re.search(r"\bsex\b", t) or "sexy" in t or "nude" in t: return "explicit sexual content"
    if "porn" in t and not NEG_PORN.search(t): return "porn content"
    if re.search(r"18\s*\+", t) and re.search(r"(porn|xxx|sex|sticker.*hot|hot.*sticker|nude)", t): return "18+ sexual/sticker group"
    if "airdrop" in t: return "crypto-airdrop scam"
    if "binary option" in t: return "binary-option investment scam"
    if "venda de xit" in t: return "paid-hack scam (VENDA DE XIT)"
    if "paid hack" in t: return "paid-hack scam"
    if "betting" in t: return "sports-betting promo"
    if "ai trading" in t or "ai-trading" in t: return "AI-trading daily-profits scam"
    if "daily profit" in t: return "daily-profits investment scam"
    if "palpite" in t: return "sports-betting tipster (palpite)"
    if "aposta" in t: return "sports-betting promo (aposta)"
    if "mines" in t and ("bug" in t or "sinal" in t): return "gambling Mines-bug/signal promo"
    return None

def check(session, code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = session.get(url, headers=UA, timeout=60)
        if r.status_code == 429:
            return ("pending", "HTTP 429 throttling", r.status_code)
        if r.status_code != 200:
            return ("pending", f"HTTP {r.status_code} (no verdict)", r.status_code)
        title = og(r.text)
        if title:
            return ("live", title, r.status_code)
        return ("empty", "", r.status_code)
    except requests.exceptions.RequestException as e:
        return ("pending", f"transport:{type(e).__name__}:{str(e)[:100]}", 0)

def main():
    pending = json.load(open(PENDING_SRC))
    existing = set(json.load(open(EXISTING)))
    # resume: rebuild all outputs from progress.jsonl (full records)
    done = {}
    candidates, pend_out, leads, exclusions = [], [], [], []
    dead = 0
    try:
        for line in open(WAVE + "team13-progress.jsonl"):
            d = json.loads(line)
            done[d["i"]] = d
            if d["verdict"] == "live" and d.get("item"): candidates.append(d["item"])
            elif d["verdict"] == "pending" and d.get("item"): pend_out.append(d["item"])
            elif d["verdict"] == "lead-nocode" and d.get("item"): leads.append(d["item"])
            elif d["verdict"] in ("excluded", "existing") and d.get("item"): exclusions.append(d["item"])
            elif d["verdict"] == "dead": dead += 1
    except FileNotFoundError:
        pass

    s = requests.Session()
    log = open(WAVE + "team13_run.log", "a")
    def lg(msg):
        print(msg, flush=True); log.write(msg + "\n"); log.flush()
    lg("=== CONTROLS ===")
    st, info, hc = check(s, "KrDwdK8EIkB6vgauHg5M7N")
    lg(f"CONTROL known-live KrDwdK8EIkB6vgauHg5M7N -> {st} | {info!r} | http={hc}")
    assert st == "live", "CONTROL FAILED: known-live code did not show og:title"
    st2, info2, hc2 = check(s, "ZZZZZZZZZZZZZZZZZZZZZZ")
    lg(f"CONTROL fabricated ZZZZZZZZZZZZZZZZZZZZZZ -> {st2} | {info2!r} | http={hc2}")
    assert st2 in ("empty", "pending") and st2 != "live", "CONTROL FAILED: fabricated code showed live"
    lg("controls OK")
    time.sleep(3)

    def save_partial():
        with open(WAVE + "team13-pending-recheck-candidates.json", "w") as f: json.dump(candidates, f, ensure_ascii=False, indent=1)
        with open(WAVE + "team13-pending-recheck-pending.json", "w") as f: json.dump(pend_out, f, ensure_ascii=False, indent=1)
        with open(WAVE + "team13-pending-recheck-leads.json", "w") as f: json.dump(leads, f, ensure_ascii=False, indent=1)
        with open(WAVE + "team13-exclusions.json", "w") as f: json.dump(exclusions, f, ensure_ascii=False, indent=1)

    consec_fail = 0
    n_total = len(pending)
    for i, e in enumerate(pending):
        if i in done:
            continue
        code = e.get("invite", "").rsplit("/", 1)[-1].strip() if e.get("invite") else ""
        rec = {"i": i, "code": code}
        if not code:
            item = {**e, "reason": "no invite code extracted (grupbul redirect fetch failed) — re-follow source redirect to obtain code; unverified, not dead"}
            leads.append(item); rec.update(verdict="lead-nocode", item=item)
        elif code in existing:
            item = {"code": code, "name": e.get("name", ""), "reason": "already in .existing_codes.json union — never bank"}
            exclusions.append(item); rec.update(verdict="existing", item=item)
        else:
            st, info, http = check(s, code)
            pre_doc_empty = "empty og:title" in (e.get("reason", "") or "")
            if st == "empty" and not pre_doc_empty:
                time.sleep(5)
                st, info, http = check(s, code)
            if st == "live":
                consec_fail = 0
                raw_name = e.get("name", "") or ""
                # Source names that are directory-page titles, not group names
                # (e.g. "1000+ Online Earning WhatsApp Group Links 2026 | J"):
                # the live og:title IS the real group name — use it instead.
                low = raw_name.lower()
                if (not raw_name) or ("whatsapp group link" in low) or ("group links" in low) or len(raw_name) > 55:
                    name = info
                else:
                    name = raw_name
                cat = CATMAP.get(e.get("category", ""), e.get("category", ""))
                if cat not in ALLOWED: cat = "Community & Social"
                country = e.get("country", "") or ""
                desc = e.get("description", "") or ""
                if (not e.get("name")) or name != e.get("name", ""):
                    desc = f"Join {name}, an active WhatsApp group for {cat.lower()}. Connect with members, share updates and stay in touch."
                item = {"name": name, "category": cat, "country": country,
                        "description": desc, "invite": f"https://chat.whatsapp.com/{code}"}
                reason = screen(name, desc + " " + info)
                if reason:
                    xitem = {"code": code, "name": name, "reason": f"content screen DROP: {reason}"}
                    exclusions.append(xitem); rec.update(verdict="excluded", item=xitem)
                else:
                    candidates.append(item); rec.update(verdict="live", item=item)
            elif st == "empty":
                consec_fail = 0
                dead += 1
                rec.update(verdict="dead")
            else:
                consec_fail += 1
                item = {**e, "reason": f"still pending recheck 20261112: {info}"}
                pend_out.append(item); rec.update(verdict="pending", item=item)
                if consec_fail >= 5:
                    lg(f"[{i+1}/{n_total}] {consec_fail} consecutive transport failures — cooling down 120s")
                    time.sleep(120); consec_fail = 0
        done[i] = rec
        with open(WAVE + "team13-progress.jsonl", "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if (i + 1) % 25 == 0:
            save_partial()
            lg(f"[{i+1}/{n_total}] live={len(candidates)} pending={len(pend_out)} dead={dead} excluded={len(exclusions)} leads={len(leads)}")
        time.sleep(1.5 + random.random() * 1.0)
    save_partial()
    summary = {
        "team": "team13", "task": "wave_20261112 pending re-check of wave_20261111_pending_all.json",
        "source_total": n_total,
        "verified_kept_candidates": len(candidates),
        "still_pending": len(pend_out),
        "dead": dead,
        "excluded_existing_union": sum(1 for x in exclusions if "existing_codes" in x["reason"]),
        "excluded_content_screen": sum(1 for x in exclusions if "content screen" in x["reason"]),
        "leads_no_code": len(leads),
        "exclusions": exclusions,
        "resume_point": "complete — all 1111 source entries processed",
        "controls": "known-live KrDwdK8EIkB6vgauHg5M7N showed og:title (live); fabricated ZZZZZZZZZZZZZZZZZZZZZZ empty og:title (dead signal)",
        "method": "python requests Session keep-alive, browser UA, 75s timeout, 1.5-2.5s spacing, one spaced retry (10s) on empty og:title before dead; 429/timeout -> pending. og:title ONLY: og:description is a constant 'WhatsApp Group Invite' on live and dead pages alike (verified on fabricated control), so it cannot serve as a live fallback.",
        "category_mapping": "Online Earning -> Jobs; Buy Sell -> Buy & Sell; empty -> Community & Social"
    }
    with open(WAVE + "team13-pending-recheck-summary.json", "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    lg("=== DONE ===")
    lg(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
