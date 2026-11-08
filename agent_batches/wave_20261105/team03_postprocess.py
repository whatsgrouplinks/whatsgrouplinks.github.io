#!/usr/bin/env python3
"""team03 post-process (run AFTER team03_verify.py finishes):
Re-applies STRENGTHENED og:title hard blocks to every record the verifier
marked verified, and rebuilds the three output files.

Why: the verifier's OG_BLOCK_RES missed a live group renamed to
'Estafadores homosexuales de bitcoin xxx' (code DbXjQLl3Exa4IS7U1dj2YG,
listed name 'Tarot y Astrología') — 'xxx' as a standalone word + 'estafador'
(scammer) were not in the patterns. Strengthened rules:
  - word-boundary xxx (\\bxxx\\b) so 'XXXTENTACION' (rapper fan group) survives
  - 'estafador' (Spanish: scammer), 'scam', 'pump', 'hyip', 'porn', 'porno',
    'onlyfans', 'escort', 'call girl', 'satta', 'sex video', 'sexo gratis',
    'money mule', 'crypto pump'
Violators move verified -> dropped (hard block: never retried, not in pending).
Also prints a drops list for the final report.
"""
import json, re, os, html

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105"
PENDING_SRC = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team35-unverified-pending.json"
PROGRESS = os.path.join(BASE, "team03-progress.jsonl")
OUT_VERIFIED = os.path.join(BASE, "team03-igrupos.json")
OUT_PENDING = os.path.join(BASE, "team03-unverified-pending.json")
OUT_LEADS = os.path.join(BASE, "team03-leads.json")

OG_BLOCK_RES = [
    re.compile(p, re.I) for p in [
        r"\bxxx\b", r"estafador", r"\bscam\b", r"porn", r"porno", r"onlyfans",
        r"escort", r"call\s*girl", r"satta", r"sex\s*video", r"sexo\s*gratis",
        r"money\s*mule", r"crypto\s*pump", r"pump\s*signal", r"hyip",
        r"hentai",
    ]
]
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)")
COUNTRY_NAMES = {
    "MX": "Mexico", "CO": "Colombia", "VE": "Venezuela", "PE": "Peru", "DO": "Dominican Republic",
    "EC": "Ecuador", "CL": "Chile", "GT": "Guatemala", "UY": "Uruguay", "BO": "Bolivia",
    "AR": "Argentina", "PY": "Paraguay", "HN": "Honduras", "SV": "El Salvador", "NI": "Nicaragua",
    "CR": "Costa Rica", "PA": "Panama", "CU": "Cuba", "ES": "Spain", "US": "United States",
    "BR": "Brazil",
}

def looks_mojibake(name):
    return ("Ã" in name) or ("â" in name) or ("ð" in name and "Ÿ" in name)

def clean_name(listed, og):
    # strip invisible format chars (soft hyphen / BOM / zero-width space) that
    # the source file carried inside words, e.g. 'Bolí\xadvar' -> 'Bolívar'
    listed = "".join(c for c in listed if c not in ("\u00ad", "\ufeff", "\u200b"))
    og = "".join(c for c in (og or "") if c not in ("\u00ad", "\ufeff", "\u200b"))
    if not listed:
        return og
    if looks_mojibake(listed):
        return og if og else listed
    if og and not re.search(r"[A-Za-zÀ-ÿ0-9]", listed):
        return og
    return listed

def make_description(name, category, country):
    cname = COUNTRY_NAMES.get(country, country if country else "International")
    cat = (category or "Other").strip()
    if cat.lower() == "other":
        return (f"Join {name}, an active WhatsApp group and community in {cname}. "
                f"Chat, share and connect with members from {cname}.")
    return (f"Join {name}, an active WhatsApp group for {cat} fans in {cname}. "
            f"Chat, share and connect with members who love {cat}.")

def main():
    attempted = {}
    with open(PROGRESS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                attempted[r["code"]] = r
    src = json.load(open(PENDING_SRC, encoding="utf-8"))
    by_code = {}
    for rec in src:
        m = CODE_RE.search(rec.get("invite", ""))
        if m:
            by_code[m.group(1)] = rec

    verified, pending, dropped = [], [], []
    for code, r in attempted.items():
        rec = by_code.get(code)
        if rec is None:
            continue
        st = r.get("status")
        if st == "verified":
            og = r.get("og_title", "")
            hit = next((rx for rx in OG_BLOCK_RES if rx.search(og or "")), None)
            if hit:
                dropped.append({"code": code, "name": rec.get("name", ""),
                                "note": f"dropped in post-process: live og:title {og!r} matched hard block {hit.pattern!r}"})
                continue
            name = clean_name((rec.get("name") or "").strip(), og)
            category = (rec.get("category") or "Other").strip() or "Other"
            country = (rec.get("country") or "International").strip() or "International"
            desc = (rec.get("description") or "").strip()
            if not desc or "igrupos" in desc.lower() or "http" in desc.lower():
                desc = make_description(name, category, country)
            image = rec.get("image") or ""
            if image and not str(image).startswith("http"):
                image = ""
            verified.append({"name": name, "category": category, "country": country,
                             "description": desc, "invite": f"https://chat.whatsapp.com/{code}",
                             "image": image})
        elif st == "pending":
            pending.append({"code": code, "name": rec.get("name", ""),
                            "note": r.get("note", "pending")})
        elif st == "dropped":
            dropped.append({"code": code, "name": rec.get("name", ""),
                            "note": r.get("note", "dropped")})
    verified.sort(key=lambda x: x["name"].lower())
    pending.sort(key=lambda x: x["code"])
    dropped.sort(key=lambda x: x["code"])
    with open(OUT_VERIFIED, "w", encoding="utf-8") as f:
        json.dump(verified, f, ensure_ascii=False, indent=2)
    with open(OUT_PENDING, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)
    with open(OUT_LEADS, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    print(f"verified={len(verified)} pending={len(pending)} dropped={len(dropped)} attempted={len(attempted)}")
    print("DROPS:")
    for d in dropped:
        print(" -", d["code"], "|", d.get("name", ""), "|", d["note"])
    with open(os.path.join(BASE, "team03-drops.json"), "w", encoding="utf-8") as f:
        json.dump(dropped, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
