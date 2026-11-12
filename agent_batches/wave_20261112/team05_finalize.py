#!/usr/bin/env python3
"""TEAM 04 finalize — run AFTER team05_mine.py has stopped.
Re-reads team05-verify.jsonl + team05-mined.jsonl, re-screens every LIVE record
with the tightened rules (adult-emoji combo, sexual-content selling, betting-
signal bots), fixes a few category misses (venda/seguidores/iptv -> Buy Sell),
dedupes, and rewrites the four output files + summary. Idempotent.
"""
import json, re, os, html

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
LEADS = os.path.join(WAVE, "leads_slice4.json")
MINED_JL = os.path.join(WAVE, "team05-mined.jsonl")
VERIFY_JL = os.path.join(WAVE, "team05-verify.jsonl")
OUT_VERIFIED = os.path.join(WAVE, "team05-leads-slice4.json")
OUT_PENDING = os.path.join(WAVE, "team05-leads-slice4-pending.json")
OUT_LEADS = os.path.join(WAVE, "team05-leads-slice4-leads.json")
OUT_SUMMARY = os.path.join(WAVE, "team05-leads-slice4-summary.json")

SCAM_TOKENS = ["b-love", "blove", "forsage", "sheyi", "holiverse",
               "meta-whale", "metawhale", "meta whale",
               "bot mines", "mines vip", "sinais mines"]
PORN_TOKENS = ["porn", "xxx", "porno", "pornô", "putaria", "nudes",
               "sexo explicito", "sexo explícito", "conteúdo adulto",
               "conteudo adulto", "videos quentes", "vídeos quentes",
               "goza", "gozar", "vendo meus conte"]
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def strip_prohibitions(t):
    if not t:
        return ""
    s = t
    s = re.sub(r"🚫\s*[^.!?;\n]{0,80}", " ", s)
    s = re.sub(r"⛔\s*[^.!?;\n]{0,80}", " ", s)
    for pat in [r"\bproibid[oa]s?\b[^.!?;\n]{0,80}",
                r"\bn[ãa]o (?:é|e) permitido\b[^.!?;\n]{0,80}",
                r"\bsem porn\w*[^.!?;\n]{0,60}",
                r"\bno porn\b[^.!?;\n]{0,60}",
                r"\bproibido porn\w*[^.!?;\n]{0,60}"]:
        s = re.sub(pat, " ", s, flags=re.I)
    return s

def screen(name, desc, ogtitle):
    blob = f"{name} {desc} {ogtitle or ''}"
    low = blob.lower()
    for tok in SCAM_TOKENS:
        if tok in low:
            return f"crypto/betting scam token '{tok}'"
    if re.search(r"\b(bet|aposta|apostas|cassino|casino)\b", low) and \
       re.search(r"lucro garantido|ganho garantido|dinheiro f[aá]cil|dobrar|2x|100% certo|certeza de ganho", low):
        return "betting-scam language"
    # adult-emoji combo: 🔞 together with a sexual emoji / sex-meetup wording
    if "🔞" in blob and re.search(r"🍆|🍑|😈|🥵|encontro|sexo|goza|putaria|acompanhante", low):
        return "adult sexual content (🔞 + sexual emoji/meetup og:title)"
    clean = strip_prohibitions(blob)
    clow = clean.lower()
    for tok in PORN_TOKENS:
        if tok in clow:
            return f"hard porn/xxx marker '{tok}'"
    if PHONE_RE.search(name) or EMAIL_RE.search(name):
        return "personal info (phone/email) in name"
    return None

def fix_category(rec):
    name = (rec.get("name") or "").lower()
    cat = rec.get("category") or "Community & Social"
    if cat in ("Friendship", "Community & Social", "Finance") and \
       ("venda" in name or "vendas" in name or "seguidor" in name or "iptv" in name):
        return "Buy Sell"
    return cat

def load_jl(path):
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
    return out

def main():
    urls = json.load(open(LEADS))
    mined = load_jl(MINED_JL)
    verify = load_jl(VERIFY_JL)
    mined_urls = {r["url"] for r in mined}
    verified, pending, exclusions = [], [], []
    dead = 0
    seen = set()
    for r in verify:
        code = r["code"]
        if r["status"] == "live" and code not in seen:
            reason = screen(r.get("name", ""), r.get("description", ""), r.get("og_title", ""))
            if reason:
                exclusions.append({"code": code, "reason": reason})
                continue
            seen.add(code)
            desc = r.get("description") or f"Join {r['name']}, a WhatsApp group listed under {r['category']}."
            rec = {"name": r["name"], "category": fix_category(r), "country": "BR",
                   "description": desc[:300], "invite": r["invite"]}
            verified.append(rec)
        elif r["status"] == "dead":
            dead += 1
        elif r["status"] == "pending" and code not in seen:
            seen.add(code)
            pending.append({"name": r["name"], "category": fix_category(r), "country": "BR",
                            "description": r.get("description") or f"Join {r['name']}, a WhatsApp group listed under {r['category']}.",
                            "invite": r["invite"],
                            "reason": "transport failure during verification (curl empty/timeout)"})
        elif r["status"] == "excluded":
            exclusions.append({"code": code, "reason": r.get("reason", "excluded")})
    for r in mined:
        if r.get("stage") == "dup-existing":
            exclusions.append({"code": r["code"], "reason": "already in groups.json (existing code)"})
    # dedupe exclusions by code, keep first
    ex_seen, ex_out = set(), []
    for e in exclusions:
        if e["code"] not in ex_seen:
            ex_seen.add(e["code"])
            ex_out.append(e)
    fetch_fail = [r["url"] for r in mined if r.get("stage") == "fetch-fail"]
    unattempted = [u for u in urls if u not in mined_urls]
    leads = fetch_fail + unattempted
    summary = {
        "team": "team05", "slice": "leads_slice4",
        "sources": ["linkado.app grupo pages"],
        "verified": len(verified), "pending": len(pending), "leads": len(leads),
        "dead": dead, "exclusions": ex_out,
        "resume": f"listings attempted: {len(mined_urls)} of {len(urls)}; next unattempted listing is index {len(urls)-len(unattempted)} in leads_slice4.json order (first unattempted URL: {unattempted[0] if unattempted else 'none — slice fully attempted'}); re-run team05_mine.py (it skips mined URLs) to continue, then re-run this finalize script.",
        "notes": [
            f"listings attempted so far: {len(mined_urls)} of {len(urls)}",
            f"listings with no invite found: {sum(1 for r in mined if r.get('stage')=='no-invite')}",
            f"listings fetch-failed (in leads file for retry): {len(fetch_fail)}",
            "linkado.app is very slow from this VM (TTFB ~15-20s) and chat.whatsapp.com ~10s+ with occasional timeouts; throughput is network-bound. Many other wave teams are fetching the same hosts concurrently.",
            "country BR for all (linkado.app is a Brazilian directory, locale pt_BR).",
            "Descriptions use the listing's own description text where present, else a template from name/category. No source name/link stored in verified entries.",
            "Finalize re-screen: adult-emoji combo (🔞 + sexual emoji/meetup wording), 'goza'/'vendo meus conteúdos' sexual-content selling, and 'bot mines' betting-signal bots excluded; 'Rifa da Vitória' kept (its description is a 🚫 prohibition, stripped before screening).",
        ],
    }
    with open(OUT_VERIFIED, "w", encoding="utf-8") as f:
        json.dump(verified, f, ensure_ascii=False, indent=1)
    with open(OUT_PENDING, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=1)
    with open(OUT_LEADS, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=1)
    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(f"FINALIZE verified={len(verified)} pending={len(pending)} leads={len(leads)} dead={dead} exclusions={len(ex_out)} attempted={len(mined_urls)}/{len(urls)}")

if __name__ == "__main__":
    main()
