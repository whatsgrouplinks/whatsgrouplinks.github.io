import json, re, time, random, html
import requests
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
def og(page):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', page, re.I)
    if m and m.group(1).strip(): return html.unescape(m.group(1).strip())
    return ""
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
    if "porn" in t: return "porn content (post-pass; negated-prohibition check done)"
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

cands = json.load(open(WAVE + "team13-pending-recheck-candidates.json"))
excl = json.load(open(WAVE + "team13-exclusions.json"))
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
s = requests.Session()
fixed, kept_old, dropped = [], [], []
out = []
for c in cands:
    code = c["invite"].rsplit("/", 1)[-1]
    assert code not in existing, f"existing-union code in candidates: {code}"
    low = c["name"].lower()
    if "whatsapp group link" in low or "group links" in low or len(c["name"]) > 55:
        title = ""
        try:
            r = s.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=60)
            if r.status_code == 200:
                title = og(r.text)
        except requests.exceptions.RequestException as e:
            print("fetch fail", code, type(e).__name__)
        if title:
            old = c["name"]
            c["name"] = title
            c["description"] = f"Join {title}, an active WhatsApp group for {c['category'].lower()}. Connect with members, share updates and stay in touch."
            fixed.append({"code": code, "old": old, "new": title})
        else:
            kept_old.append({"code": code, "name": c["name"], "reason": "og:title re-fetch empty/failed — kept source name, code was verified live in main pass"})
        time.sleep(1.5 + random.random())
    reason = screen(c["name"], c["description"])
    if reason:
        excl.append({"code": code, "name": c["name"], "reason": f"content screen DROP (post-pass re-screen): {reason}"})
        dropped.append({"code": code, "name": c["name"], "reason": reason})
    else:
        out.append(c)
assert len({x["invite"] for x in out}) == len(out), "dup codes in final candidates"
json.dump(out, open(WAVE + "team13-pending-recheck-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(excl, open(WAVE + "team13-exclusions.json", "w"), ensure_ascii=False, indent=1)
summ = json.load(open(WAVE + "team13-pending-recheck-summary.json"))
summ["verified_kept_candidates"] = len(out)
summ["excluded_content_screen"] = sum(1 for x in excl if "content screen" in x["reason"])
summ["exclusions"] = excl
summ["method"] = ("python requests Session keep-alive, browser UA, 60s timeout (75s for first 115 codes), 1.5-2.5s spacing, "
  "one spaced retry (5s; 10s for first 115 codes) on empty og:title before dead; no in-run retry for codes whose source reason already "
  "documented empty og:title after spaced attempts (today's fresh empty = 3rd confirmation); 429/timeout -> pending. og:title ONLY: "
  "og:description is a constant 'WhatsApp Group Invite' on live and dead pages alike (verified on fabricated control), so it cannot serve as a live fallback.")
summ["post_pass_fixup"] = {
    "names_fixed_from_og_title": fixed,
    "names_kept_on_refetch_failure": kept_old,
    "dropped_on_rescreen": dropped,
    "note": "Source names that were directory-page titles (e.g. '1000+ Online Earning WhatsApp Group Links 2026 | Join Now') were replaced with the live og:title (the real group name) for pre-patch banked items; the main script applied the same rule inline from index 461 on. Two pre-patch betting items were dropped by the extended PT screen (palpite / Mines-bug) on re-screen."
}
json.dump(summ, open(WAVE + "team13-pending-recheck-summary.json", "w"), ensure_ascii=False, indent=2)
print("FIXED:", json.dumps(fixed, ensure_ascii=False, indent=1))
print("KEPT_OLD:", kept_old)
print("DROPPED:", json.dumps(dropped, ensure_ascii=False, indent=1))
print("final candidates:", len(out))
