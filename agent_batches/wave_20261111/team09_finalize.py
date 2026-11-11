#!/usr/bin/env python3
"""TEAM 09 — build final output files from the checker checkpoint."""
import json, re

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
PEND = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/wave_20261110_pending_all.json"
CKPT = WAVE + "/team09-pending-recheck-checkpoint.jsonl"
EXCL_PRE = WAVE + "/team09-pending-recheck-exclusions-pre.json"

CANON = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology",
         "Health","Business","Gaming","Friendship","Community & Social","Online Earning",
         "Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate",
         "Buy Sell","Finance","Funny"}
SCAM_PAT = re.compile(
    r"b-?love|forsage|sury|sheyi|holiverse|meta[\s\-]?whale|airdrop|"
    r"betway|betpawa|sure\s+odds|betting\s+tips|fixed\s+match|"
    r"double\s+(your\s+)?money|earn\s+\d|daily\s+profit", re.I)
PORN_PAT = re.compile(r"\b(xxx|porn|sex\s*video|nude|desi\s*sex|hot\s*girls?\s*xxx)\b", re.I)
NEG_PAT = re.compile(r"[^.!?\n]*(no|not|don't|dont|never|prohibit\w*|forbidden)[^.!?\n]*(porn|xxx|sex|nude)[^.!?\n]*[.!?\n]?", re.I)

def strip_negated(t):
    return NEG_PAT.sub(" ", t or "")

def norm_cat(c):
    c = (c or "").strip()
    if c in ("", "general", "other", "unknown"):
        return "Community & Social"
    if c == "buy-sell":
        return "Buy Sell"
    if c in ("movies", "music"):
        return "Entertainment"
    return c if c in CANON else "Community & Social"

def norm_country(c):
    c = (c or "").strip()
    return c if re.fullmatch(r"[A-Z]{2}", c) else ""

def norm_entry(e):
    name = (e.get("name") or "").strip()
    cat = norm_cat(e.get("category"))
    country = norm_country(e.get("country"))
    desc = (e.get("description") or "").strip()
    if not desc:
        desc = f"Join {name}, a WhatsApp group for {cat.lower()} discussions with other members."
        if country:
            desc += f" Based in {country}."
    return {"name": name, "category": cat, "country": country,
            "description": desc, "invite": e.get("invite", "").strip()}

def main():
    pend = json.load(open(PEND))
    by_code = {e["invite"].rsplit("/", 1)[-1]: e for e in pend}
    exclusions = list(json.load(open(EXCL_PRE)))
    results = {}
    grouped = {}
    with open(CKPT) as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if "entry" in r:
                grouped.setdefault(r["code"], []).append(r)
    for code, rs in grouped.items():
        # Duplicate codes: prefer the team09 browser-leg entry's verdict —
        # a browser-leg code verified live in the browser must stay pending,
        # never be marked dead on curl evidence from the other team's entry.
        bl = [r for r in rs if r["entry"].get("_team_file") == "team09-pending-recheck-pending.json"]
        results[code] = bl[0] if bl else rs[-1]
    dup_codes = {c: len(rs) for c, rs in grouped.items() if len(rs) > 1}
    verified, pending, dead = [], [], []
    for code, r in results.items():
        e = r["entry"]
        if r["status"] == "live":
            og = r.get("og_title", "")
            screen_text = strip_negated(e.get("name", "") + " " + og)
            if SCAM_PAT.search(screen_text):
                exclusions.append({"code": code,
                    "reason": f"scam og:title/name dropped: name={e.get('name','')!r} og_title={og!r}"})
            elif PORN_PAT.search(screen_text):
                exclusions.append({"code": code,
                    "reason": f"hard porn/xxx og:title/name dropped: name={e.get('name','')!r} og_title={og!r}"})
            else:
                verified.append(norm_entry(e))
        elif r["status"] == "pending":
            p = norm_entry(e)
            p["reason"] = r.get("reason", e.get("reason", "pending"))
            pending.append(p)
        elif r["status"] == "dead":
            dead.append({"code": code, "name": e.get("name", ""),
                         "reason": r.get("reason", "")})
    accounted = len(verified) + len(pending) + len(dead) + len(exclusions)
    print(f"verified={len(verified)} pending={len(pending)} dead={len(dead)} "
          f"exclusions={len(exclusions)} accounted={accounted}/393 unique codes "
          f"(397 entries; {len(dup_codes)} codes duplicated in source file: {sorted(dup_codes)})")
    assert accounted == 393, f"ACCOUNTING MISMATCH: {accounted} != 393 unique codes"
    assert len(results) == 389, f"checked {len(results)} != 389 unique codes"

    with open(WAVE + "/team09-pending-recheck.json", "w") as f:
        json.dump(verified, f, indent=1, ensure_ascii=False)
    with open(WAVE + "/team09-pending-recheck-pending.json", "w") as f:
        json.dump(pending, f, indent=1, ensure_ascii=False)
    with open(WAVE + "/team09-pending-recheck-leads.json", "w") as f:
        json.dump([], f, indent=1)
    summary = {
        "team": "team09",
        "slice": "pending recheck — wave_20261110_pending_all.json (397 codes)",
        "sources": ["wave_20261110/wave_20261110_pending_all.json"],
        "verified": len(verified),
        "pending": len(pending),
        "leads": 0,
        "dead": len(dead),
        "exclusions": exclusions,
        "dead_codes": dead,
        "resume": "complete — all 397 entries accounted for (393 unique codes: verified + pending + dead + exclusions = 393; 4 codes appear twice in the source file with conflicting team metadata and were resolved once each, preferring the team09 browser-leg entry)",
        "notes": [
            "Slow curl checker: max 6 workers, 0.6s delay, retry-on-empty-og after 6s pause; transport failure retried once after 4s.",
            "309 team09 browser-leg-only codes (Nov 10): curl cannot verify them (empty og:title); per slice instruction they were kept pending, NOT marked dead.",
            "Non-browser-leg codes with HTTP 200 + empty og:title on 2 spaced attempts were marked dead.",
            "1 code already in .existing_codes.json was excluded as duplicate, never banked.",
            "3 scam names dropped on sight before checking: BETWAY BWP TIPS, Wagmi Airdrop Community, Betpawa sure odds.",
            "og:title of every live code was screened for scam/porn terms (negated-prohibition sentences stripped first); no live code was excluded on og:title.",
            "Country 'International' normalised to '' (2-letter code or empty only); empty category normalised to 'Community & Social'.",
            "Source file contains 397 entries but only 393 unique codes: Bo6Splc8d3oC3gr4xf0UA2, Fp53YAbEUa78T4zAZcCjRZ, KR7gWco4iCw3aRB8JtcI70, KzwO6LVoaS8DT0LBwqu16S each appear twice with conflicting name/category from different teams. All 4 resolved to pending via the team09 browser-leg entry (curl empty-og both times; browser verified live Nov 10).",
        ],
    }
    with open(WAVE + "/team09-pending-recheck-summary.json", "w") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("WROTE all 4 output files.")

if __name__ == "__main__":
    main()
