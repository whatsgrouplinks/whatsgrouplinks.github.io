#!/usr/bin/env python3
"""Team 01 - assemble screened candidates from verified-live codes."""
import json, os, re, html as htmlmod

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
ALLOWED_CATS = ["Gaming", "Education", "Online Earning", "Community & Social", "Business",
                "Friendship", "Finance", "Buy Sell", "Islamic", "Entertainment", "Jobs",
                "Technology", "Funny", "Sports", "Health", "News"]

# --- load verify results ---
verify = []
for f in ["team01_verify.json", "team01_verify_shard0.json", "team01_verify_shard1.json",
          "team01_verify_shard2.json", "team01_verify_new0.json", "team01_verify_new1.json",
          "team01_verify_new2.json"]:
    p = os.path.join(WAVE, f)
    if os.path.exists(p):
        verify.extend(json.load(open(p)))
live = {r["code"]: r for r in verify if r["status"] == "live"}
print("live codes:", len(live))

ctx = {}
lk = json.load(open(os.path.join(WAVE, "team01_linkado_codes.json")))
for c, v in lk.items():
    ctx[c] = v

# --- screening ---
PROHIBITION_RES = [
    r"[^.!?\n]*\bproibid[oa]s?\b[^.!?\n]*",
    r"[^.!?\n]*\bn[aã]o envie\b[^.!?\n]*",
    r"[^.!?\n]*\bnao envie\b[^.!?\n]*",
    r"[^.!?\n]*\bn[aã]o [eé] permitido\b[^.!?\n]*",
    r"[^.!?\n]*inappropriate content[^.!?\n]*",
    r"[^.!?\n]*\bdo not (share|send|post)\b[^.!?\n]*",
]
def strip_prohibitions(text):
    for rx in PROHIBITION_RES:
        text = re.sub(rx, " ", text, flags=re.I)
    return text

DROP_RES = [
    r"\bporn\b", r"\bxxx\b", r"\bsexo\b", r"\bsexual\b", r"\bsex\b",
    r"escort", r"acompanhante", r"garota de programa", r"onlyfans",
    r"\bnudes?\b", r"novinh[ao]s?", r"putaria", r"vazad[oa]s?", r"vazamento",
    r"\bsexy\b", r"cam-girl", r"camgirl", r"\bhookup\b",
    r"b-?love", r"forsage", r"s?heyi\b", r"airdrop",
    r"dinheiro gr[áa]tis", r"free money", r"ganhe dinheiro",
    r"dobrar (seu )?dinheiro", r"renda garantida",
    r"\+18", r"🔞", r"🍆", r"🍑",
]
def drop_reason(text):
    t = strip_prohibitions(text)
    for rx in DROP_RES:
        if re.search(rx, t, flags=re.I):
            return rx
    return None

def clean_desc(text, name):
    text = htmlmod.unescape(text or "")
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"chat\.whatsapp\.com/\S+", " ", text)
    text = re.sub(r"\+\d[\d\s\-()]{9,}", " ", text)  # phone numbers
    text = re.sub(r"\s+", " ", text).strip(" .-|")
    # keep at most 2 sentences
    parts = re.split(r"(?<=[.!?])\s+", text)
    parts = [p.strip() for p in parts if p.strip()]
    text = " ".join(parts[:2]).strip()
    if len(text) > 220:
        text = text[:217].rsplit(" ", 1)[0] + "..."
    if not text or len(text) < 12:
        text = f"Join this WhatsApp group to chat and connect with other members about {name}."
    return text

candidates, screened_out, pending = [], [], []
for code, r in sorted(live.items()):
    v = ctx.get(code, {})
    name = (r.get("title") or "").strip() or v.get("linkado_name", "")
    name = re.sub(r"\s+", " ", name).strip()
    desc_src = (v.get("linkado_desc") or "") + " " + (r.get("description") or "")
    blob = f"{name} {desc_src}"
    reason = drop_reason(blob)
    if reason:
        screened_out.append({"code": code, "name": name, "reason": reason,
                             "linkado_desc": v.get("linkado_desc", "")})
        continue
    cats = v.get("categories", ["Community & Social"])
    cat = next((c for c in cats if c != "Community & Social"), cats[0])
    if cat not in ALLOWED_CATS:
        cat = "Community & Social"
    desc = clean_desc(v.get("linkado_desc") or r.get("description") or "", name)
    if drop_reason(name + " " + desc):
        screened_out.append({"code": code, "name": name, "reason": "desc-drop",
                             "linkado_desc": v.get("linkado_desc", "")})
        continue
    candidates.append({"name": name, "category": cat, "country": "BR",
                       "description": desc,
                       "invite": f"https://chat.whatsapp.com/{code}"})

json.dump(candidates, open(os.path.join(WAVE, "team01-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(screened_out, open(os.path.join(WAVE, "team01_screened_out.json"), "w"), indent=1, ensure_ascii=False)
print("candidates:", len(candidates))
print("screened out:", len(screened_out))
for s in screened_out:
    print("  DROP", s["code"], s["reason"], s["name"][:70])
for c in candidates:
    print("  KEEP", c["name"][:70], "|", c["category"], "|", c["description"][:90])
